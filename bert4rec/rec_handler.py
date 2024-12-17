from typing import List, Tuple

from dto import Prediction

import torch
import numpy as np

from recbole.model.abstract_recommender import SequentialRecommender
from recbole.data.interaction import Interaction


class RecommendationHandler:
    def __init__(self, dataset, model: SequentialRecommender) -> None:
        self.dataset = dataset
        self.model = model

    def build_recos(self, item_sequence: List[int], k: int) -> List[Prediction]:
        """
            Generates recommendations based on a sequence of external item indices.

            Args:
                item_sequence: A list of external item indices.

            Returns:
                A list of type Prediction.
        """

        scores, inner_iid = self._predict(
            self.dataset.token2id(self.dataset.iid_field, item_sequence),
            k
        )

        scores = scores.view(k).tolist()
        indices = inner_iid.view(k).tolist()
        raw_iid = [self.dataset.id2token(self.dataset.iid_field, indices)]

        return [Prediction(iid, score) for iid, score in list(zip(raw_iid[0], scores))]

    def _predict(self, item_sequence: List[int], k: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
            Calculates the top k items for a given sequence of internal indices.

            Args:
                item_sequence: A list of internal indices of items.
                k: amount of items.

            Returns:
                A tuple containing two lists:
                    - The first list contains the internal indices of the top k items.
                    - The second list contains the scores of these items.
        """

        self.model.eval()
        with torch.no_grad():

            inter = self._prepare_interaction_data(item_sequence)

            scores = self.model.full_sort_predict(inter)
            scores = scores.view(-1, self.dataset.item_num)
            scores[:, 0] = -np.inf

        item_score, item_inner_iid = torch.topk(scores, k)
        return item_score, item_inner_iid

    def _prepare_interaction_data(self, item_sequence: List[int]) -> Interaction:
        return Interaction({
            "item_id_list": self._pad_item_sequence_to_max_length(item_sequence),
            "item_length": torch.tensor([len(item_sequence)])
        }).to(self.model.device)

    def _pad_item_sequence_to_max_length(self, item_sequence: list):
        # Если последовательность меньше максимальной длины предметов модели
        new_tensor = torch.zeros((1, self.model.max_seq_length), dtype=torch.int64)
        new_tensor[:, :len(item_sequence)] = torch.tensor([item_sequence])
        return new_tensor
