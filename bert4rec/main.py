from rec_handler import RecommendationHandler
from recbole.quick_start import load_data_and_model


if __name__ == "__main__":
    config, model, dataset, *_ = load_data_and_model(
        model_file="./saved/BERT4Rec-Dec-17-2024_15-29-26.pth"
    )

    r_handler = RecommendationHandler(dataset, model)
    p = r_handler.build_recos(["72133", "22457", "85049E", "17090D", "84763"], 30)
    print(p)
