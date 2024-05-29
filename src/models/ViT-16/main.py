import argparse, sys, os, yaml
import torch.nn as nn
from torchvision.models import vit_b_16, ViT_B_16_Weights
from torchvision.datasets import FGVCAircraft, Flowers102
import torch.optim as optim
import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.utils import main, load_model, freeze_layers

def freeze_layers_vit(model):
    for name, param in model.named_parameters():
        if 'head' not in name:
            param.requires_grad = False

if __name__ == "__main__":

    parser = argparse.ArgumentParser("")
    parser.add_argument("--config", required = True, type = str, help = "Path to the configuration file")
    parser.add_argument("--run_name", required = False, type = str, help = "Name of the run")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = load_model(vit_b_16, weights = ViT_B_16_Weights.IMAGENET1K_V1)

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    learning_rate = config["training"]["lr"]
    frozen_layers = config["training"]["frozen_layers"]
    momentum = config["training"]["optimizer"]["momentum"]
    weight_decay = config["training"]["optimizer"]["weight_decay"]
    step_size = config["training"]["scheduler"]["step_size"]
    gamma = config["training"]["scheduler"]["gamma"]
    num_classes = config["data"]["num_classes"]

    model.num_classes = num_classes
    freeze_layers_vit(model = model)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(filter(lambda p: p.requires_grad, model.parameters()),
                          lr = learning_rate,
                          momentum = momentum,
                          weight_decay = weight_decay)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size = step_size, gamma = gamma)

    main(args = args,
         model = model,
         dataset_function = FGVCAircraft,
         dataset_name = "FGVCAircraft",
         num_classes = num_classes,
         criterion = criterion,
         optimizer = optimizer,
         scheduler = scheduler,
         device = device,
         config = config)
