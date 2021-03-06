import os

from .base import add_misc_options, add_cuda_options, adding_cuda, ArgumentParser
from .tools import save_args
from .dataset import add_dataset_options
from .model import add_model_options, parse_modelname
from .checkpoint import construct_checkpointname


def add_training_options(parser):
    group = parser.add_argument_group('Training options')
    group.add_argument("--batch_size", type=int, required=True, help="size of the batches")
    group.add_argument("--num_epochs", type=int, required=True, help="number of epochs of training")
    group.add_argument("--lr", type=float, required=True, help="AdamW: learning rate")
    group.add_argument("--snapshot", type=int, required=True, help="frequency of saving model/viz")

    # parameter for beta annealing
    group.add_argument("--beta_max", type=float, required=False, default=2e-6, help="max beta value when beta annealing")

    # parameters for sigmoid annraling
    group.add_argument("--beta_sigmoid_weight", type=float, required=False, default=1., help="hyper parameter for sigmoid annraling")
    group.add_argument("--beta_sigmoid_bias", type=float, required=False, default=0., help="hyper parameter for sigmoid annraling")

    # parameters for cyclic annealing
    group.add_argument("--beta_cycle_ratio", type=float, required=False, default=0.5, help="hyper parameter for cyclic annealing")
    group.add_argument("--beta_cycle_n", type=int, required=False, default=4, help="hyper parameter for cyclic annealing")
    group.add_argument("--data_aug", type=float, required=False, default=1.0, help="decides data augmentation if True")
def parser():
    parser = ArgumentParser()

    # misc options
    add_misc_options(parser)

    # cuda options
    add_cuda_options(parser)
    
    # training options
    add_training_options(parser)

    # dataset options
    add_dataset_options(parser)

    # model options
    add_model_options(parser)

    opt = parser.parse_args()
    
    # remove None params, and create a dictionnary
    parameters = {key: val for key, val in vars(opt).items() if val is not None}

    # parse modelname
    ret = parse_modelname(parameters["modelname"])
    parameters["modeltype"], parameters["archiname"], parameters["losses"] = ret
    
    # update lambdas params
    lambdas = {}
    for loss in parameters["losses"]:
        lambdas[loss] = opt.__getattribute__(f"lambda_{loss}")
    parameters["lambdas"] = lambdas
    if lambdas['kl'] == 'sigmoid':
        parameters['beta_sigmoid'] = True
        parameters['beta_cycle'] = False
    elif lambdas['kl'] == 'cycle':
        parameters['beta_sigmoid'] = False
        parameters['beta_cycle'] = True
    elif 'e-' in lambdas['kl']:
        parameters['beta_sigmoid'] = False
        parameters['beta_cycle'] = False
        lambdas['kl'] = float(lambdas['kl'])

    
    if "folder" not in parameters:
        parameters["folder"] = construct_checkpointname(parameters, parameters["expname"])

    os.makedirs(parameters["folder"], exist_ok=True)
    save_args(parameters, folder=parameters["folder"])

    adding_cuda(parameters)
    
    return parameters
