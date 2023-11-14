from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abc
import tensorflow as tf
import numpy as np

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.environments import suite_gym
from tf_agents.trajectories import time_step as ts

from Thymio.Thymio import Thymio
from tdmclient import ClientAsync


class ThymioEnvironment(py_environment.PyEnvironment):
    def __init__(self, client_addr=None, client_port=None, client_password=None):
        super().__init__()
        self.client_addr = client_addr
        self.client_port = client_port
        self.client_password = client_password
        self.client = ClientAsync(tdm_addr=self.client_addr, tdm_port=self.client_port, password=self.client_password)
        self.thymio = Thymio(self.client)
        # TODO: I think this needs to be a single action which takes a parameter of left speed and right speed?
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=1, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(1,), dtype=np.int32, minimum=0, name='observation')
        self._state = 0
        self.episode_ended = False

    def observation_spec(self):
        return self._observation_spec

    def action_spec(self):
        return self._action_spec

    def _reset(self):
        # TODO: May also need to end and restart the Thymio Sim
        self._state = 0
        self._episode_ended = False
        self.thymio.disconnect()
        return ts.restart(np.array([self._state], dtype=np.int32))

    def _step(self, action):
        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start a new episode.
            return self.reset()

        # TODO define the actions (I think there is only one action, which is to set the motors
        # Need to add a catch here to end the simulation if the Thymio hits the wall
        # TODO: Make sure v actually changes ever step and update this to use self._state
        if self.thymio.node.v.prox.horizontal[2] > 4000:
            self._episode_ended = True
        else:
            self.thymio.motors(100, 100)

        if self._episode_ended:
            # TODO: Create a reward function
            reward = 1
            return ts.termination(np.array([self._state], dtype=np.int32), reward)
        else:
            return ts.transition(np.array([self._state], dtype=np.int32), reward=0.0, discount=1.0)

