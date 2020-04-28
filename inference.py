"""
Run a trained agent and get generated maps
"""
import model
from stable_baselines import PPO2
import numpy as np

import time
from utils import make_vec_envs

def infer(game, representation, model_path, **kwargs):
    """
     - max_trials: The number of trials per evaluation.
     - infer_kwargs: Args to pass to the environment.
    """
    env_name = '{}-{}-v0'.format(game, representation)
    if "small" in game:
        model.FullyConvPolicy = model.FullyConvPolicySmallMap
        kwargs['cropped_size'] = 8
    elif "medium" in game:
        model.FullyConvPolicy = model.FullyConvPolicyBigMap
        kwargs['cropped_size'] = 12
    elif "large" in game:
        model.FullyConvPolicy = model.FullyConvPolicyBigMap
        kwargs['cropped_size'] = 16
    kwargs['render'] = False
    agent = PPO2.load(model_path)
    env = make_vec_envs(env_name, representation, None, 1, **kwargs)
    obs = env.reset()
    dones = False
    for i in range(kwargs.get('trials', 1)):
        while not dones:
            action, _ = agent.predict(obs)
            obs, _, dones, info = env.step(action)
            env.render(mode='human')
            if kwargs.get('verbose', False):
                print(info[0])
            if dones:
                break
        time.sleep(0.2)
    return env, obs

################################## MAIN ########################################
game = 'small_fair_rts'
representation = 'narrow'
model_path = 'models/{}/{}/model_1.pkl'.format(game, representation)
kwargs = {
    'change_percentage': 0.4,
    'trials': 1,
    'verbose': False
}


if __name__ == '__main__':
    env, obs = infer(game, representation, model_path, **kwargs)
    print("-------------------------")
    res = [[np.argmax(item) for item in row] for row in obs[0]]
    for row in res:
        print(row)
