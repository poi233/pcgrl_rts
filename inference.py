"""
Run a trained agent and get generated maps
"""
import model
from stable_baselines import PPO2

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
        kwargs['cropped_size'] = 10
    elif "medium" in game:
        model.FullyConvPolicy = model.FullyConvPolicyBigMap
        kwargs['cropped_size'] = 18
    elif "large" in game:
        model.FullyConvPolicy = model.FullyConvPolicyBigMap
        kwargs['cropped_size'] = 34


    kwargs['render'] = True

    agent = PPO2.load(model_path)
    env = make_vec_envs(env_name, representation, None, 1, **kwargs)
    obs = env.reset()
    dones = False
    for i in range(kwargs.get('trials', 1)):
        while not dones:
            action, _ = agent.predict(obs)
            obs, _, dones, info = env.step(action)
            print()
            if kwargs.get('verbose', False):
                print(info[0])
            if dones:
                break
        time.sleep(0.2)
    return obs

################################## MAIN ########################################
game = 'rts'
size = 'medium'
style = 'fair'
representation = 'narrow'
model_path = 'models/{}_{}_{}/{}/model_1.pkl'.format(size, style, game, representation)
kwargs = {
    'change_percentage': 0.4,
    'trials': 1,
    'verbose': True
}


if __name__ == '__main__':
    obs = infer(game, representation, model_path, **kwargs)
    print(obs)
