import os

import numpy as np
from PIL import Image

from gym_pcgrl.envs.helper import get_range_reward, get_tile_locations, \
    calc_num_regions, calc_certain_tile, calc_longest_path, run_dikjstra
from gym_pcgrl.envs.probs.problem import Problem

"""
Generate a  RTS map where two player can play.

Args:
    target_enemy_dist: enemies should be at least this far from the player on spawn
"""


class RTSProblem(Problem):
    """
    The constructor is responsible of initializing all the game parameters
    """

    def __init__(self):
        super().__init__()
        self._width = 8
        self._height = 8
        self._prob = {"solid": 0, "empty": 0.7, "base": 0.02, "resource": 0.1, "chock_point": 0.18}
        self._border_tile = "solid"

        self._target_base = 2
        self._min_resource = 1
        self._max_resource = 4
        self._max_chock_points = self._width * 2

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

    """
    Get a list of all the different tile names

    Returns:
        string[]: that contains all the tile names
    """

    def get_tile_types(self):
        return ["solid", "empty", "base", "resource", "chock_point"]

    """
    Adjust the parameters for the current problem

    Parameters:
        width (int): change the width of the problem level
        height (int): change the height of the problem level
        probs (dict(string, float)): change the probability of each tile
        intiialization, the names are "empty", "solid"
        target_path (int): the current path length that the episode turn when it reaches
        rewards (dict(string,float)): the weights of each reward change between the new_stats and old_stats
    """

    def adjust_param(self, **kwargs):
        super().adjust_param(**kwargs)


        self._max_resource = kwargs.get('max_resource', self._max_resource)
        self._max_chock_points = kwargs.get('max_chock_points', self._max_chock_points)

        rewards = kwargs.get('rewards')
        if rewards is not None:
            for t in rewards:
                if t in self._rewards:
                    self._rewards[t] = rewards[t]

    """
    Get the current stats of the map

    Returns:
        dict(string,any): stats of the current map to be used in the reward, episode_over, debug_info calculations.
        The used status are "reigons": number of connected empty tiles, "path-length": the longest path across the map
    """

    def get_stats(self, map):
        map_locations = get_tile_locations(map, self.get_tile_types())
        map_stats = {
            "base_count": calc_certain_tile(map_locations, ["base"]),
            "resource_count": calc_certain_tile(map_locations, ["resource"]),
            "chock_point": calc_certain_tile(map_locations, ["chock_point"]),
            "base_distance": 0,
            # "base_space": 0,
            # "asymmetry": 0,
            "resource_distance": 0,
            # "resource_clustering": 0,
            # "path_overlapping": 0,
            "region": calc_num_regions(map, map_locations, ["empty", "base", "resource"])
        }
        if map_stats["base_count"] == 2:
            # calculate distance
            b1_x, b1_y = map_locations["base"][0]
            b2_x, b2_y = map_locations["base"][1]
            dikjstra1, _ = run_dikjstra(b1_x, b1_y, map, ["empty", "base", "resource"])
            map_stats["base_distance"] = max(map_stats["base_distance"], dikjstra1[b2_y][b2_x])
            # calculate resource distance
            if map_stats["resource_count"] >= self._min_resource and map_stats["resource_count"] <= self._max_resource:
                dikjstra2, _ = run_dikjstra(b2_x, b2_y, map, ["empty", "base", "resource"])
                resources = []
                resources.extend(map_locations["resource"])
                dist1 = 10000
                dist2 = 10000
                for r_x, r_y in resources:
                    if dikjstra1[r_y][r_x] > 0:
                        dist1 = min(dist1, dikjstra1[r_y][r_x])
                    if dikjstra2[r_y][r_x] > 0:
                        dist2 = min(dist2, dikjstra2[r_y][r_x])
                map_stats["resource_distance"] = 1 - abs(dist1 - dist2)
        return map_stats

    """
    Get the current game reward between two stats

    Parameters:
        new_stats (dict(string,any)): the new stats after taking an action
        old_stats (dict(string,any)): the old stats before taking an action

    Returns:
        float: the current reward due to the change between the old map stats and the new map stats
    """

    def get_reward(self, new_stats, old_stats):
        # longer path is rewarded and less number of regions is rewarded
        rewards = {
            "base_count": get_range_reward(new_stats["base_count"], old_stats["base_count"], self._target_base, self._target_base),
            "base_distance": get_range_reward(new_stats["base_distance"], old_stats["base_distance"], self._width / 2, self._width * 2),
            # "base_space": get_range_reward(new_stats["base_space"], old_stats["base_space"], 0, 10),
            # "asymmetry": get_range_reward(new_stats["asymmetry"], old_stats["asymmetry"], 0, 5),
            "resource_count": get_range_reward(new_stats["resource_count"], old_stats["resource_count"], self._min_resource, self._max_resource),
            "resource_distance": get_range_reward(new_stats["resource_distance"], old_stats["resource_distance"], 0, 1),
            # "resource_clustering": get_range_reward(new_stats["resource_clustering"], old_stats["resource_clustering"], 0, 5),
            # "path_overlapping": get_range_reward(new_stats["path_overlapping"], old_stats["path_overlapping"], 0, 10),
            "chock_point": get_range_reward(new_stats["chock_point"], old_stats["chock_point"], 0, self._max_chock_points),
            "region": get_range_reward(new_stats["region"], old_stats["region"], 1, 1)
        }
        # calculate the total reward
        return rewards["base_count"] * self._rewards["base_count"] + \
            rewards["base_distance"] * self._rewards["base_distance"] + \
            rewards["resource_count"] * self._rewards["resource_count"] + \
            rewards["region"] * self._rewards["region"] + \
            rewards["resource_distance"] * self._rewards["resource_distance"] + \
            rewards["chock_point"] * self._rewards["chock_point"]
        # rewards["asymmetry"] * self._rewards["asymmetry"] + \
        # rewards["base_space"] * self._rewards["base_space"] + \
        # rewards["resource_clustering"] * self._rewards["resource_clustering"] + \
        # rewards["path_overlapping"] * self._rewards["path_overlapping"] + \

    """
    Uses the stats to check if the problem ended (episode_over) which means reached
    a satisfying quality based on the stats

    Parameters:
        new_stats (dict(string,any)): the new stats after taking an action
        old_stats (dict(string,any)): the old stats before taking an action

    Returns:
        boolean: True if the level reached satisfying quality based on the stats and False otherwise
    """

    def get_episode_over(self, new_stats, old_stats):
        return new_stats["base_count"] == self._target_base and \
               new_stats["resource_count"] >= self._min_resource and \
               new_stats["resource_count"] <= self._max_resource and \
               new_stats["base_distance"] > 2 and \
               new_stats["resource_distance"] >= 0
    """
    Get any debug information need to be printed

    Parameters:
        new_stats (dict(string,any)): the new stats after taking an action
        old_stats (dict(string,any)): the old stats before taking an action

    Returns:
        dict(any,any): is a debug information that can be used to debug what is
        happening in the problem
    """

    def get_debug_info(self, new_stats, old_stats):
        return {
            "base_count": new_stats["base_count"],
            "base_distance": new_stats["base_distance"],
            # "base_space": new_stats["base_space"],
            # "asymmetry": new_stats["asymmetry"],
            "resource_count": new_stats["resource_count"],
            "resource_distance": new_stats["resource_distance"],
            # "resource_clustering": new_stats["resource_clustering"],
            # "path_overlapping": new_stats["path_overlapping"],
            "chock_point": new_stats["chock_point"],
            "region": new_stats["region"]
            #
            # "player": new_stats["player"],
            # "key": new_stats["key"],
            # "door": new_stats["door"],
            # "enemies": new_stats["enemies"],
            # "regions": new_stats["regions"],
            # "nearest-enemy": new_stats["nearest-enemy"],
            # "path-length": new_stats["path-length"]
        }

    """
    Get an image on how the map will look like for a specific map

    Parameters:
        map (string[][]): the current game map

    Returns:
        Image: a pillow image on how the map will look like using the binary graphics
    """
    def render(self, map):
        if self._graphics == None:
            self._graphics = {
                "solid": Image.open(os.path.dirname(__file__) + "/rts/impassable.png").convert('RGBA'),
                "empty": Image.open(os.path.dirname(__file__) + "/rts/passable.png").convert('RGBA'),
                "base": Image.open(os.path.dirname(__file__) + "/rts/base.png").convert('RGBA'),
                "resource": Image.open(os.path.dirname(__file__) + "/rts/mineral.png").convert('RGBA'),
                "chock_point": Image.open(os.path.dirname(__file__) + "/rts/impassable.png").convert('RGBA'),
            }
        return super().render(map)
