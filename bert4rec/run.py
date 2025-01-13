import logging
from logging import getLogger
from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.model.sequential_recommender import BERT4Rec
from recbole.trainer import Trainer
from recbole.utils import init_seed, init_logger


if __name__ == "__main__":

    params = {
        "data_path": "./dataset",
        "USER_ID_FIELD": "user_id",
        "ITEM_ID_FIELD": "item_id",
        "TIME_FIELD": "timestamp",
        "train_neg_sample_args": None,
        "load_col": {"inter": ["user_id", "item_id", "timestamp"]},
        "neg_sampling": None,
        "epochs": 50,
        "learning_rate": 0.001,
        "eval_args": {
            "split": {"RS": [9, 1, 0]},
            "group_by": "user",
            "order": "TO",
            "mode": "full"},
        }

    config = Config(model="BERT4Rec", dataset="data", config_dict=params)
    init_seed(config["seed"], config["reproducibility"])

    init_logger(config)
    logger = getLogger()

    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    logger.addHandler(c_handler)

    logger.info(config)

    dataset = create_dataset(config)
    logger.info(dataset)

    train_data, valid_data, test_data = data_preparation(config, dataset)

    model = BERT4Rec(config, train_data.dataset).to(config['device'])
    logger.info(model)

    trainer = Trainer(config, model)

    best_valid_score, best_valid_result = trainer.fit(train_data, valid_data)
