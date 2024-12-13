import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import paramiko
import matplotlib.pyplot as plt

class PIDPolicyNetwork(nn.Module):
    """
    Neural network to output constrained PID parameters.
    """
    def __init__(self, output_dim=3):
        super(PIDPolicyNetwork, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(1, 64),  # Dummy input of size 1
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim * 2)  # Outputs mean and log-variance for [P, I, D]
        )

    def forward(self, x):
        output = self.model(x)
        mean, log_var = torch.chunk(output, 2, dim=-1)  # Split output into mean and log-variance

        # Apply scaling to mean to constrain to [-8191, 8191]
        mean = torch.tanh(mean)
        return mean, log_var





def evaluate_policy(pid_params, ssh, remote_csv_path="/root/acquisition_data.csv", local_csv_path="acquisition_data.csv"):
    return -np.sum(pid_params**2)
    """
    Evaluate the PID parameters by:
    1. Running the PID control executable with the given parameters.
    2. Running the signal capture executable to generate a CSV file.
    3. Retrieving the CSV file and calculating the reward based on signal stability.

    Args:
        pid_params (list or array): PID parameters [Kp, Ki, Kd].
        ssh (paramiko.SSHClient): Open SSH connection.
        remote_csv_path (str): Path to the CSV file on the remote device.
        local_csv_path (str): Path to save the CSV file locally.

    Returns:
        float: Reward value (negative standard deviation of the signal).
    """
    try:
        # Step 1: Run the PID executable with the PID parameters
        pid_vals = pid_params[0] * 2**13
        pid_command = f"/root/pid {int(pid_vals[0])} {int(pid_vals[1])} {int(pid_vals[2])}"
        stdin, stdout, stderr = ssh.exec_command(pid_command)
        print(stdout.read().decode())
        print(stderr.read().decode())

        # Step 2: Run the signal capture executable
        capture_command = "/root/capture_signal"
        stdin, stdout, stderr = ssh.exec_command(capture_command)
        print(stdout.read().decode())
        print(stderr.read().decode())

        # Step 3: Retrieve the CSV file via SCP
        with ssh.open_sftp() as sftp:
            sftp.get(remote_csv_path, local_csv_path)
        print(f"File successfully copied to {local_csv_path}")

        # Step 4: Calculate reward based on signal stability
        signal_data = np.loadtxt(local_csv_path, delimiter=",")
        reward = -np.std(signal_data)  # Negative standard deviation as reward
        return reward

    except Exception as e:
        print(f"Error during evaluation: {e}")
        return -float('inf')  # Return a large negative reward for failure


def train_policy():
    # Connection details
    red_pitaya_host = "205.208.56.192"
    red_pitaya_user = "root"
    red_pitaya_password = "root"

    # Initialize SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(red_pitaya_host, username=red_pitaya_user, password=red_pitaya_password)
    print("SSH connection established.")
    losses = []
    rewards = []
    try:
        # Initialize policy network
        policy = PIDPolicyNetwork(output_dim=3)
        optimizer = optim.Adam(policy.parameters(), lr=1e-3)

        num_iterations = 500
        dummy_input = torch.FloatTensor([[1]])  # Dummy input for the policy
        for iteration in range(num_iterations):
            # Step 1: Forward pass through the policy network
            mean, log_var = policy(dummy_input)
            std = torch.exp(0.5 * log_var)
            pid_params = mean + std * torch.randn_like(mean)  # Sample PID parameters

            # Debugging outputs
            print(f"Iteration {iteration + 1}")
            print(f"Mean: {mean.detach().numpy()}, Std: {std.detach().numpy()}")
            print(f"Sampled PID Params: {pid_params.detach().numpy()}")

            # Step 2: Evaluate the reward
            reward = evaluate_policy(pid_params.detach().numpy(), ssh)
            rewards.append(reward)  # Store the reward

            print(f"Reward: {reward}")

            # Step 3: Normalize rewards for stability
            normalized_reward = (reward - np.mean(rewards)) / (np.std(rewards) + 1e-8)

            # Step 4: Compute log-probabilities of actions
            log_prob = -0.5 * ((pid_params - mean) / std).pow(2) - log_var - 0.5 * np.log(2 * np.pi)
            log_prob = log_prob.sum(dim=-1)  # Sum over all actions (P, I, D)

            # Step 5: Compute the policy gradient loss
            loss = -(log_prob * normalized_reward)
            reward_tensor = torch.tensor(reward, dtype=torch.float32)
            loss = -reward_tensor
            losses.append(loss.item())

            # Debugging outputs for loss
            print(f"Loss: {loss.item()}")

            # Step 6: Perform backpropagation and optimizer step
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print("Training complete!")

    finally:
        # Close SSH connection
        ssh.close()
        plt.figure(figsize=(12, 6))

        # Plot Losses
        plt.subplot(1, 2, 1)
        plt.plot(losses, label="Loss", color="blue", linewidth=2)
        plt.title("Loss During Training", fontsize=14)
        plt.xlabel("Iteration", fontsize=12)
        plt.ylabel("Loss", fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend(fontsize=12)

        # Plot Rewards
        plt.subplot(1, 2, 2)
        plt.plot(rewards, label="Reward", color="green", linewidth=2)
        plt.title("Reward During Training", fontsize=14)
        plt.xlabel("Iteration", fontsize=12)
        plt.ylabel("Reward", fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend(fontsize=12)

        # Adjust layout and show the plots
        plt.tight_layout()
        plt.show()
        print("SSH connection closed.")


if __name__ == "__main__":
    train_policy()
