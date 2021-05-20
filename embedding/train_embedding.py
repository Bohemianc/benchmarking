from embedding import Config as conf
from embedding.models.TransE import TransE
import os
import tensorflow as tf


def trainModel(
    path,
    work_threads=2,
    train_times=10,
    nbatches=128,
    dimension=50,
    alpha=0.01,
    lmbda=0.01,
    bern=1,
    margin=1,
    model=TransE,
):
    # warnings.filterwarnings("ignore")
    os.environ['KMP_WARNINGS'] = '0' # it works.
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    con = conf.Config()

    con.set_in_path(path)
    con.set_work_threads(work_threads)  # 4 allocate threads for each batch sampling
    con.set_train_times(train_times)  # 100
    con.set_nbatches(nbatches)  # 100
    con.set_alpha(alpha)
    con.set_lmbda(lmbda)
    con.set_bern(bern)
    con.set_margin(margin)
    con.set_dimension(dimension)  # 100
    con.set_ent_neg_rate(1)
    con.set_rel_neg_rate(0)
    con.set_opt_method("Adagrad")

    con.get_test_file()
    con.set_test_link_prediction(False)
    con.set_test_triple_classification(False)

    con.init()
    con.set_model(model)

    con.run()

    return (
        con.get_parameters_by_name("ent_embeddings"),
        con.get_parameters_by_name("rel_embeddings"),
    )
