#pip install tensorflow==1.15
#Install stable-baselines as described in the documentation

import model
from model import FullyConvPolicyBigMap, FullyConvPolicySmallMap, CustomPolicyBigMap, CustomPolicySmallMap
from utils import get_exp_name, max_exp_idx, load_model, make_vec_envs
from stable_baselines import PPO2
from stable_baselines.results_plotter import load_results, ts2xy

import tensorflow as tf
import numpy as np
import os

n_steps = 0
log_dir = './'
best_mean_reward, n_steps = -np.inf, 0

def callback(_locals, _globals):
    """
    Callback called at each step (for DQN an others) or after n steps (see ACER or PPO2)
    :param _locals: (dict)
    :param _globals: (dict)
    """
    global n_steps, best_mean_reward
    # Print stats every 1000 calls
    if (n_steps + 1) % 10 == 0:
        x, y = ts2xy(load_results(log_dir), 'timesteps')
        if len(x) > 100:
           #pdb.set_trace()
            mean_reward = np.mean(y[-100:])
            print(x[-1], 'timesteps')
            print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(best_mean_reward, mean_reward))

            # New best model, we save the agent here
            if mean_reward > best_mean_reward:
                best_mean_reward = mean_reward
                # Example for saving best model
                print("Saving new best model")
                _locals['self'].save(os.path.join(log_dir, 'best_model.pkl'))
            else:
                print("Saving latest model")
                _locals['self'].save(os.path.join(log_dir, 'latest_model.pkl'))
        else:
            print('{} monitor entries'.format(len(x)))
            pass
    n_steps += 1
    # Returning False will stop training early
    return True


def train(game, representation, experiment, steps, n_cpu, render, logging, **kwargs):
    env_name = '{}-{}-v0'.format(game, representation)
    exp_name = get_exp_name(game, representation, experiment, **kwargs)
    resume = kwargs.get('resume', False)
    if representation == 'wide':
        policy = FullyConvPolicyBigMap
        if "small" or "medium" in game:
            policy = FullyConvPolicySmallMap
    else:
        policy = CustomPolicyBigMap
        if "small" or "medium" in game:
            policy = CustomPolicySmallMap
    if "small" in game:
        kwargs['cropped_size'] = 8
    elif "medium" in game:
        kwargs['cropped_size'] = 12
    n = max_exp_idx(exp_name)
    global log_dir
    if not resume:
        n = n + 1
    log_dir = 'runs/{}_{}_{}'.format(exp_name, n, 'log')
    if not resume:
        os.mkdir(log_dir)
    else:
        model = load_model(log_dir)
    kwargs = {
        **kwargs,
        'render_rank': 0,
        'render': render,
    }
    used_dir = log_dir
    if not logging:
        used_dir = None
    env = make_vec_envs(env_name, representation, log_dir, n_cpu, **kwargs)
    if not resume or model is None:
        model = PPO2(policy, env, verbose=1, tensorboard_log="./runs")
    else:
        model.set_env(env)
    if not logging:
        model.learn(total_timesteps=int(steps), tb_log_name=exp_name)
    else:
        model.learn(total_timesteps=int(steps), tb_log_name=exp_name, callback=callback)

def train_all():
    for game in games:
        for representation in representations:
            train(game, representation, experiment, steps, n_cpu, render, logging, **kwargs)

################################## MAIN ########################################
sizes = ["small", "medium", "large"]
styles = ["fair", "fun"]
representations = ["narrow", "turtle", "wide"]
games = []
for size in sizes:
    for style in styles:
        games.append("%s_%s_rts" % (size, style))
experiment = None
steps = 1e7
render = False
logging = True
n_cpu = 50
kwargs = {
    'resume': False
}

if __name__ == '__main__':
    game = 'area_control_small_rts'
    representation = 'narrow'
    train(game, representation, experiment, steps, n_cpu, render, logging, **kwargs)

    # train_all()
    # games = ['area_control_small_rts', 'base_small_rts', 'resource_small_rts', 'small_fair_rts']
    # representation = 'narrow'
    # for game in games:
    #     train(game, representation, experiment, steps, n_cpu, render, logging, **kwargs)
