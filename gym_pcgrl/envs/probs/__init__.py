from gym_pcgrl.envs.probs.binary_prob import BinaryProblem
from gym_pcgrl.envs.probs.ddave_prob import DDaveProblem
from gym_pcgrl.envs.probs.mdungeon_prob import MDungeonProblem
from gym_pcgrl.envs.probs.sokoban_prob import SokobanProblem
from gym_pcgrl.envs.probs.zelda_prob import ZeldaProblem
from gym_pcgrl.envs.probs.rts_prob import RTSProblem
from gym_pcgrl.envs.probs.small_fair_rts_prob import SmallFairRTSProblem
from gym_pcgrl.envs.probs.small_fun_rts_prob import SmallFunRTSProblem
from gym_pcgrl.envs.probs.medium_fair_rts_prob import MediumFairRTSProblem
from gym_pcgrl.envs.probs.medium_fun_rts_prob import MediumFunRTSProblem
from gym_pcgrl.envs.probs.large_fair_rts_prob import LargeFairRTSProblem
from gym_pcgrl.envs.probs.larget_fun_rts_prob import LargeFunRTSProblem



# all the problems should be defined here with its corresponding class
PROBLEMS = {
    "binary": BinaryProblem,
    "ddave": DDaveProblem,
    "mdungeon": MDungeonProblem,
    "sokoban": SokobanProblem,
    "zelda": ZeldaProblem,
    "rts": RTSProblem,
    "small_fair_rts": SmallFairRTSProblem,
    "small_fun_rts": SmallFunRTSProblem,
    "medium_fair_rts": MediumFairRTSProblem,
    "medium_fun_rts": MediumFunRTSProblem,
    "large_fair_rts": LargeFairRTSProblem,
    "large_fun_rts": LargeFunRTSProblem
}
