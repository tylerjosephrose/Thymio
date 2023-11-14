from Environment import ThymioEnvironment
from tf_agents.environments import utils


environment = ThymioEnvironment()
utils.validate_py_environment(environment, episodes=5)
