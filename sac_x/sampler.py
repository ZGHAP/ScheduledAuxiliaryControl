import torch
import gym
from sac_x.replay_buffer import SharedReplayBuffer
from torch.multiprocessing import current_process


class Sampler:
    def __init__(self,
                 actor: torch.nn.Module,
                 replay_buffer: SharedReplayBuffer,
                 scheduler,
                 argp,
                 logger=None):

        self.actor = actor
        self.replay_buffer = replay_buffer
        self.scheduler = scheduler
        self.num_trajectories = argp.num_trajectories
        self.trajectory_length = argp.num_trajectories
        self.schedule_switch = argp.schedule_switch
        self.log_every = argp.log_interval

        self.logger = logger
        if argp.num_worker > 1:
            self.pid = current_process()._identity[0]  # process ID
        else:
            self.pid = 1

        # self.env = gym.make("Hopper-v2")
        # self.env = gym.make("Swimmer-v2")
        # self.env = gym.make("Pendulum-v0")
        # self.env = gym.make("HalfCheetah-v2")

    def run(self):
        for i in range(self.num_trajectories):
            states, actions, rewards, action_log_probs = [], [], [], []
            h = 0
            obs = torch.tensor(self.env.reset(), dtype=torch.float)
            for t in range(self.trajectory_length):
                # Sample an intention from the scheduler
                if t % self.schedule_switch == 0:
                    intention_idx = self.scheduler.sample_intention()
                    h += 1

                # Create an action with intention idx
                # Track: state action rewards behaviour-logprobs schedule-decisions
                # Update scheduler

                # mean, log_std = self.actor.forward(obs)
                # action, action_log_prob = self.actor.action_sample(mean, log_std)
                # next_obs, reward, done, _ = self.env.step(action.detach().cpu())
                # next_obs = torch.tensor(next_obs, dtype=torch.float)
                # reward = reward.clone().detach()
                # states.append(obs)
                # actions.append(action)
                # rewards.append(reward)
                # action_log_probs.append(action_log_prob)
                # obs = next_obs

                # if self.render:
                #     self.env.render()

            # turn lists into tensors
            states = torch.stack(states)
            actions = torch.stack(actions)
            rewards = torch.stack(rewards)
            action_log_probs = torch.stack(action_log_probs)

            if self.pid == 1 and self.logger is not None and i % self.log_every == 0:
                self.logger.add_scalar(scalar_value=rewards.mean(), tag="Reward/train")

            self.replay_buffer.push(states, actions.detach(), rewards, action_log_probs.detach())