import statistics
import datetime
from typing import Any 

from flamapy.metamodels.fm_metamodel.models import Feature 

from montecarlo_framework.models import Problem
from montecarlo_framework.models.feature_model import FMConfiguration
from montecarlo_framework.problems.configuration_based_analyses import ConfigurationState


class OptimizeConfigurationState(ConfigurationState):

    def __init__(self, configuration: FMConfiguration, attributes: dict[Feature, dict[str, Any]], problem: Problem = None) -> None:
        super().__init__(configuration)
        self.attributes = attributes
        self.problem = problem

    def set_problem(self, problem: Problem) -> None:
        self.problem = problem

    def heuristic(self) -> float:
        return 0

    def configuration_transition_function(self, configuration: FMConfiguration) -> 'ConfigurationState':
        return OptimizeConfigurationState(configuration, self.attributes, self.problem)

    def reward(self) -> float:
        if not self.configuration.is_valid_configuration():
            return -1000
        else:
            return self.objective_function()

    def objective_function(self) -> float:
        today = datetime.date.today()
        last_update_dates = []
        user_ratings = []
        for feature in self.configuration.get_selected_features():
            if feature in self.attributes.keys():
                last_update_dates.append((today - self.attributes[feature]['UpdateDate'].date()).days)
                user_ratings.append(self.attributes[feature]['UserRating'])
        # normalization
        # if last_update_dates:
        #     min_date = min(last_update_dates)
        #     range_date = max(last_update_dates) - min_date 
        #     if range_date > 0:
        #         normalized_dates = list(map(lambda x: (x - min_date)/range_date, last_update_dates))
        #     else:
        #         normalized_dates = last_update_dates
        #     median_dates = statistics.median(normalized_dates)
        # else:
        #     median_dates = 0

        # normalization
        # if user_ratings:
        #     min_ratings = min(user_ratings)
        #     range_ratings = max(user_ratings) - min_ratings
        #     if range_ratings > 0:
        #         normalized_ratings = list(map(lambda x: (x - min_ratings)/range_ratings, user_ratings))
        #     else:
        #         normalized_ratings = user_ratings
        #     median_ratings = statistics.median(normalized_ratings)
        # else:
        #     median_ratings = 0
        median_dates = statistics.median(last_update_dates) if last_update_dates else 0
        median_ratings = statistics.median(user_ratings) if user_ratings else 0
        #print(f'Median dates: {median_dates}')
        #print(f'Median ratings: {median_ratings}')
        return -median_dates * 1000 + median_ratings * 1000


class FindingOptimumConfigProblem(Problem):

    @staticmethod
    def get_name() -> str:
        return 'Finding optimum configurations in the AAFM Framework'

    def __init__(self, initial_state: ConfigurationState):
        super().__init__()
        self.initial_state = initial_state

    def get_initial_state(self) -> ConfigurationState:
        return self.initial_state