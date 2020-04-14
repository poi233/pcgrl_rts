from gym_pcgrl.envs.probs import RTSProblem


class LargeFunRTSProblem(RTSProblem):
    def __init__(self):
        super().__init__()
        self._width = 16
        self._height = 16

        self._min_resource = self._width / 8 * 2
        self._max_resource = self._width / 2 * 2
        self._max_chock_points = self._width * 2
        self._resource_distance_diff = self._width / 8 * 2

        self._rewards = {
            "base_count": 6,
            "base_distance": 2,
            # "base_space": 2,
            # "asymmetry": 1,
            "resource_count": 4,
            "resource_distance": 1,
            # "resource_clustering": 1,
            # "path_overlapping": 2,
            "chock_point": 3,
            "region": 6
        }
