#######################################################################
# Copyright (C) 2017 Shangtong Zhang(zhangshangtong.cpp@gmail.com)    #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
#######################################################################

import logging
from agent import *
from component import *
from utils import *
import model.action_conditional_video_prediction as acvp

## cart pole

def dqn_cart_pole():
    game = 'CartPole-v0'
    config = Config()
    config.task_fn = lambda: ClassicalControl(game, max_steps=200)
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, 0.001)
    config.network_fn = lambda state_dim, action_dim: FCNet(state_dim, 64, action_dim)
    # config.network_fn = lambda state_dim, action_dim: DuelingFCNet(state_dim, 64, action_dim)
    config.policy_fn = lambda: GreedyPolicy(epsilon=1.0, final_step=10000, min_epsilon=0.1)
    config.replay_fn = lambda: Replay(memory_size=10000, batch_size=10)
    config.discount = 0.99
    config.target_network_update_freq = 200
    config.exploration_steps = 1000
    config.logger = Logger('./log', logger)
    config.double_q = True
    # config.double_q = False
    run_episodes(DQNAgent(config))

def a2c_cart_pole():
    config = Config()
    name = 'CartPole-v0'
    # name = 'MountainCar-v0'
    task_fn = lambda log_dir: ClassicalControl(name, max_steps=200, log_dir=log_dir)
    config.num_workers = 5
    config.task_fn = lambda: ParallelizedTask(task_fn, config.num_workers,
                                              log_dir=get_default_log_dir(a2c_cart_pole.__name__))
    config.optimizer_fn = lambda params: torch.optim.Adam(params, 0.001)
    config.network_fn = lambda state_dim, action_dim: ActorCriticFCNet(state_dim, 64, action_dim)
    config.policy_fn = SamplePolicy
    config.discount = 0.99
    config.logger = Logger('./log', logger)
    config.gae_tau = 1.0
    config.entropy_weight = 0.01
    config.rollout_length = 5
    run_iterations(A2CAgent(config))

def categorical_dqn_cart_pole():
    game = 'CartPole-v0'
    config = Config()
    config.task_fn = lambda: ClassicalControl(game, max_steps=200)
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, 0.001)
    config.network_fn = lambda state_dim, action_dim: \
        CategoricalFCNet(state_dim, action_dim, config.categorical_n_atoms)
    config.policy_fn = lambda: GreedyPolicy(epsilon=0.1, final_step=10000, min_epsilon=0.1)
    config.replay_fn = lambda: Replay(memory_size=10000, batch_size=10)
    config.discount = 0.99
    config.target_network_update_freq = 200
    config.exploration_steps = 100
    config.logger = Logger('./log', logger, skip=True)
    config.categorical_v_max = 100
    config.categorical_v_min = -100
    config.categorical_n_atoms = 50
    run_episodes(CategoricalDQNAgent(config))

def quantile_regression_dqn_cart_pole():
    config = Config()
    config.task_fn = lambda: ClassicalControl('CartPole-v0', max_steps=200)
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, 0.001)
    config.network_fn = lambda state_dim, action_dim: \
        QuantileFCNet(state_dim, action_dim, config.num_quantiles)
    config.policy_fn = lambda: GreedyPolicy(epsilon=0.1, final_step=10000, min_epsilon=0.1)
    config.replay_fn = lambda: Replay(memory_size=10000, batch_size=10)
    config.discount = 0.99
    config.target_network_update_freq = 200
    config.exploration_steps = 100
    config.logger = Logger('./log', logger, skip=True)
    config.num_quantiles = 20
    run_episodes(QuantileRegressionDQNAgent(config))

def n_step_dqn_cart_pole():
    config = Config()
    task_fn = lambda log_dir: ClassicalControl('CartPole-v0', max_steps=200, log_dir=log_dir)
    config.num_workers = 5
    config.task_fn = lambda: ParallelizedTask(task_fn, config.num_workers)
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, 0.001)
    config.network_fn = lambda state_dim, action_dim: FCNet(state_dim, 64, action_dim)
    config.policy_fn = lambda: GreedyPolicy(epsilon=1.0, final_step=10000, min_epsilon=0.1)
    config.discount = 0.99
    config.target_network_update_freq = 200
    config.rollout_length = 5
    config.logger = Logger('./log', logger)
    run_iterations(NStepDQNAgent(config))

## Atari games

def dqn_pixel_atari(name):
    config = Config()
    config.history_length = 4
    config.task_fn = lambda: PixelAtari(name, frame_skip=4, history_length=config.history_length,
                                        log_dir=get_default_log_dir(dqn_pixel_atari.__name__))
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, lr=0.00025, alpha=0.95, eps=0.01)
    config.network_fn = lambda state_dim, action_dim: ConvNet(config.history_length, action_dim, gpu=0)
    # config.network_fn = lambda state_dim, action_dim: DuelingConvNet(config.history_length, action_dim)
    config.policy_fn = lambda: GreedyPolicy(epsilon=1.0, final_step=1000000, min_epsilon=0.1)
    config.replay_fn = lambda: Replay(memory_size=1000000, batch_size=32, dtype=np.uint8)
    config.state_normalizer = ImageNormalizer()
    config.reward_normalizer = SignNormalizer()
    config.discount = 0.99
    config.target_network_update_freq = 10000
    config.exploration_steps= 50000
    config.logger = Logger('./log', logger)
    # config.double_q = True
    config.double_q = False
    run_episodes(DQNAgent(config))

def a2c_pixel_atari(name):
    config = Config()
    config.history_length = 4
    config.num_workers = 5
    task_fn = lambda log_dir: PixelAtari(name, frame_skip=4, history_length=config.history_length, log_dir=log_dir)
    config.task_fn = lambda: ParallelizedTask(task_fn, config.num_workers, log_dir=get_default_log_dir(a2c_pixel_atari.__name__))
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, lr=0.0007)
    config.network_fn = lambda state_dim, action_dim: ActorCriticConvNet(
        config.history_length, action_dim, gpu=3)
    config.policy_fn = SamplePolicy
    config.state_normalizer = ImageNormalizer()
    config.reward_normalizer = SignNormalizer()
    config.discount = 0.99
    config.use_gae = False
    config.gae_tau = 0.97
    config.entropy_weight = 0.01
    config.rollout_length = 5
    config.gradient_clip = 0.5
    config.logger = Logger('./log', logger, skip=True)
    run_iterations(A2CAgent(config))

def categorical_dqn_pixel_atari(name):
    config = Config()
    config.history_length = 4
    config.task_fn = lambda: PixelAtari(name, frame_skip=4, history_length=config.history_length,
                                        log_dir=get_default_log_dir(categorical_dqn_pixel_atari.__name__))
    config.optimizer_fn = lambda params: torch.optim.Adam(params, lr=0.00025, eps=0.01 / 32)
    config.network_fn = lambda state_dim, action_dim: CategoricalConvNet(config.history_length, action_dim, config.categorical_n_atoms, gpu=0)
    config.policy_fn = lambda: GreedyPolicy(epsilon=1.0, final_step=1000000, min_epsilon=0.1)
    config.replay_fn = lambda: Replay(memory_size=1000000, batch_size=32, dtype=np.uint8)
    config.discount = 0.99
    config.state_normalizer = ImageNormalizer()
    config.reward_normalizer = SignNormalizer()
    config.target_network_update_freq = 10000
    config.exploration_steps= 50000
    config.logger = Logger('./log', logger)
    config.double_q = False
    config.categorical_v_max = 10
    config.categorical_v_min = -10
    config.categorical_n_atoms = 51
    run_episodes(CategoricalDQNAgent(config))

def quantile_regression_dqn_pixel_atari(name):
    config = Config()
    config.history_length = 4
    config.task_fn = lambda: PixelAtari(name, frame_skip=4, history_length=config.history_length,
                                        log_dir=get_default_log_dir(quantile_regression_dqn_pixel_atari.__name__))
    config.optimizer_fn = lambda params: torch.optim.Adam(params, lr=0.00005, eps=0.01 / 32)
    config.network_fn = lambda state_dim, action_dim: QuantileConvNet(config.history_length, action_dim, config.num_quantiles, gpu=0)
    config.policy_fn = lambda: GreedyPolicy(epsilon=1.0, final_step=1000000, min_epsilon=0.01)
    config.replay_fn = lambda: Replay(memory_size=1000000, batch_size=32, dtype=np.uint8)
    config.state_normalizer = ImageNormalizer()
    config.reward_normalizer = SignNormalizer()
    config.discount = 0.99
    config.target_network_update_freq = 10000
    config.exploration_steps= 50000
    config.logger = Logger('./log', logger)
    config.double_q = False
    config.num_quantiles = 200
    run_episodes(QuantileRegressionDQNAgent(config))

def n_step_dqn_pixel_atari(name):
    config = Config()
    config.history_length = 4
    task_fn = lambda log_dir: PixelAtari(name, frame_skip=4, history_length=config.history_length, log_dir=log_dir)
    config.num_workers = 16
    config.task_fn = lambda: ParallelizedTask(task_fn, config.num_workers,
                                              log_dir=get_default_log_dir(n_step_dqn_pixel_atari.__name__))
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, lr=0.00025, alpha=0.95, eps=0.01)
    config.network_fn = lambda state_dim, action_dim: ConvNet(config.history_length, action_dim, gpu=0)
    config.policy_fn = lambda: GreedyPolicy(epsilon=1.0, final_step=1000000, min_epsilon=0.1)
    config.state_normalizer = ImageNormalizer()
    config.reward_normalizer = SignNormalizer()
    config.discount = 0.99
    config.target_network_update_freq = 10000
    config.rollout_length = 5
    config.logger = Logger('./log', logger)
    run_iterations(NStepDQNAgent(config))

def dqn_ram_atari(name):
    config = Config()
    config.task_fn = lambda: RamAtari(name, no_op=30, frame_skip=4,
                                      log_dir=get_default_log_dir(dqn_ram_atari.__name__))
    config.optimizer_fn = lambda params: torch.optim.RMSprop(params, lr=0.00025, alpha=0.95, eps=0.01)
    config.network_fn = lambda state_dim, action_dim: FCNet(state_dim, 64, action_dim, gpu=2)
    config.policy_fn = lambda: GreedyPolicy(epsilon=0.1, final_step=1000000, min_epsilon=0.1)
    config.replay_fn = lambda: Replay(memory_size=100000, batch_size=32, dtype=np.uint8)
    config.state_normalizer = RescaleNormalizer(1.0 / 128)
    config.reward_normalizer = SignNormalizer()
    config.discount = 0.99
    config.target_network_update_freq = 10000
    config.max_episode_length = 0
    config.exploration_steps= 100
    config.logger = Logger('./log', logger)
    config.double_q = True
    # config.double_q = False
    run_episodes(DQNAgent(config))

## continuous control

def ppo_continuous():
    config = Config()
    config.num_workers = 5
    task_fn = lambda log_dir: Pendulum(log_dir=log_dir)
    # task_fn = lambda log_dir: Roboschool('RoboschoolInvertedPendulum-v1', log_dir=log_dir)
    # task_fn = lambda log_dir: Roboschool('RoboschoolAnt-v1', log_dir=log_dir)
    config.task_fn = lambda: ParallelizedTask(task_fn, config.num_workers, log_dir=get_default_log_dir(ppo_continuous.__name__))
    config.actor_network_fn = lambda state_dim, action_dim: GaussianActorNet(state_dim, action_dim)
    config.critic_network_fn = lambda state_dim, action_dim: GaussianCriticNet(state_dim)
    config.actor_optimizer_fn = lambda params: torch.optim.Adam(params, 0.001)
    config.critic_optimizer_fn = lambda params: torch.optim.Adam(params, 0.001)
    config.state_normalizer = RunningStatsNormalizer()
    config.discount = 0.99
    config.use_gae = True
    config.gae_tau = 0.97
    config.gradient_clip = 0.5
    config.rollout_length = 20
    config.optimize_epochs = 4
    config.ppo_ratio_clip = 0.2
    config.logger = Logger('./log', logger)
    run_iterations(PPOAgent(config))

def ddpg_continuous():
    config = Config()
    log_dir = get_default_log_dir(ddpg_continuous.__name__)
    config.task_fn = lambda: Pendulum(log_dir=log_dir)
    # config.task_fn = lambda: Roboschool('RoboschoolInvertedPendulum-v1')
    # config.task_fn = lambda: Roboschool('RoboschoolReacher-v1')
    # config.task_fn = lambda: Roboschool('RoboschoolHopper-v1')
    # config.task_fn = lambda: Roboschool('RoboschoolAnt-v1')
    # config.task_fn = lambda: Roboschool('RoboschoolWalker2d-v1')
    config.actor_network_fn = lambda state_dim, action_dim: DeterministicActorNet(state_dim, action_dim)
    config.critic_network_fn = lambda state_dim, action_dim: DeterministicCriticNet(state_dim, action_dim)
    config.actor_optimizer_fn = lambda params: torch.optim.Adam(params, lr=1e-4)
    config.critic_optimizer_fn = lambda params: torch.optim.Adam(params, lr=1e-4)
    config.replay_fn = lambda: HighDimActionReplay(memory_size=1000000, batch_size=64)
    config.discount = 0.99
    config.random_process_fn = \
        lambda action_dim: OrnsteinUhlenbeckProcess(size=action_dim, theta=0.15, sigma=0.3,
                                         n_steps_annealing=100000)
    config.min_memory_size = 64
    config.target_network_mix = 1e-3
    config.gradient_clip = 1.0
    config.logger = Logger('./log', logger)
    run_episodes(DDPGAgent(config))

if __name__ == '__main__':
    mkdir('data')
    mkdir('data/video')
    mkdir('log')
    os.system('export OMP_NUM_THREADS=1')
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)

    # dqn_cart_pole()
    # a2c_cart_pole()
    # categorical_dqn_cart_pole()
    # quantile_regression_dqn_cart_pole()
    # n_step_dqn_cart_pole()

    # dqn_pixel_atari('BreakoutNoFrameskip-v4')
    # a2c_pixel_atari('BreakoutNoFrameskip-v4')
    # categorical_dqn_pixel_atari('BreakoutNoFrameskip-v4')
    # quantile_regression_dqn_pixel_atari('BreakoutNoFrameskip-v4')
    # n_step_dqn_pixel_atari('BreakoutNoFrameskip-v4')
    # dqn_ram_atari('Breakout-ramNoFrameskip-v4')

    # ddpg_continuous()
    # ppo_continuous()

    # acvp.train('PongNoFrameskip-v4')

