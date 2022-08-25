import pandas as pd
from sklearn.cluster import KMeans
from random import randint as rn
from .prepare_data import DataPreparation
import pickle


class ActiveLearning:
    """
    A class to represent Active Learning

    Attributes
    ----------
    X: DataFrame
        DataFrame contains all features except target column
    y: Series
        series that contain target data
    images: list
        list that contain image urls
    data_prep: DataPreparation
        DataPreparation object for preparing data for active learning processes
    main_dataframe: DataFrame
        DataFrame before the preprocess operations for active learning applied


    Methods
    ----------
    set_X(new_df)
        sets X to given dataframe
    set_y(new_list)
        sets y to given series
    get_data(data)
        returns prepared X and prepared y
    create_diverse_sample(data, n_cluster, n)
        creates a sample using clustering
    least_confidence(pdist)
        calculates confident level of items in terms of prediction probabilities
    create_sample(pdist_total, size_uncertain, n_cluster, n):
        create a sample using clustering for diversity and selecting most uncertain items
    ask_to_user(indexes)
        finds image urls of items for asking the users
    active_learning_labeling(model, index_labeled_data, X, y, size_uncertain, n_cluster, n)
        applies labeling processes of active learning
    active_learning_updating(index_labeled_data, y, asked_idx, labels_asked)
        applies updating processes of active learning
    fit(model, labeled_data, X, y)
        fits the given model with labeled data and tries to predict unlabeled ones
    scoring(model, data)
        scores the items
    """

    def __init__(self) -> None:
        """
        Parameters
        ----------
        X: DataFrame
            DataFrame contains all features except target column
        y: Series
            series that contain target data
        images: list
            list that contain image urls
        data_prep: DataPreparation
            DataPreparation object for preparing data for active learning processes
        main_dataframe: DataFrame
            DataFrame before the preprocess operations for active learning applied
        """
        self.X = None
        self.y = None
        self.images = None
        self.data_prep = DataPreparation()
        self.data_prep.load_data()
        self.main_dataframe = self.data_prep.dataframe
    
    def set_X(self, new_df):
        """ Sets X to given dataframe """
        self.X = new_df
    
    def set_y(self, new_list):
        """ Sets y to given series """
        self.y = new_list
    
    def get_data(self, data):
        """ Gets dataframe, returns X and y from Data Preparation class """
        self.X, self.y = self.data_prep.prepare_data(data)
        return self.X, self.y

    def get_data2(self, data):
        return self.data_prep.get_transformed_data(data)

    def create_diverse_sample(self, data, n_cluster, n):
        """
        Applies clustering and takes the most n popular items for each cluster

        Parameters
        ----------
        data: DataFrame
            data used for clustering
        n_cluster: int
            creates n_cluster times cluster
        n: int
            takes n most popular elements for each clusters

        Returns
        ----------
        dict
            a dictionary that contains indexes and image urls of items {index: image_url}
        """

        data_c = data.copy()
        k_means = KMeans(n_clusters= n_cluster)
        k_means.fit(data_c)
        data_c["pred"] = k_means.predict(data_c)
        
        indexes = []
        for i in range(n_cluster):
            list_ = (list(self.main_dataframe.loc[data_c[data_c.pred ==i].index].sort_values(by="review_nums", ascending =False)[:(n + 200)].index))
            for j in range(n):
               indexes.append([(list_[rn(0, len(list_)-1)])])

        sample_dict = {}
        for i in indexes:
            for j in i:
                sample_dict[j] = self.main_dataframe.loc[j].image_url

        return sample_dict

    def least_confidence(self, pdist):
        """ Finds confidence level for given prediction probabilities returns confidence score """
        return (pdist.size / (pdist.size - 1)) * (1 - pdist.max())

    def create_sample(self, X, pdist_total, size_uncertain, n_cluster, n):
        """
        Applies least_confidence to total prediction probabilities to find most uncertain items

        Parameters
        ----------
        size_uncertain: int
            total size of uncertain elements
        n: int
            takes n element for each clusters

        Returns
        ----------
        list
            indexes of size_uncertain most uncertain items
        """
        uncertanity_sample = []

        # gets least confidence scores
        for i in pdist_total:
            uncertanity_sample.append(self.least_confidence(i))
        uncertanity_sample_df = pd.DataFrame(uncertanity_sample, index= X.index)

        # takes items which confidence level is greater than 0.7
        indx_uncertain= uncertanity_sample_df[uncertanity_sample_df[0] > 0.70].index

        # create a sample with the least confident items
        dict_ = self.create_diverse_sample(X.loc[indx_uncertain], n_cluster, n)
        
        return dict_.keys()

    def ask_to_user(self, indexes):
        """ Finds image urls of items for asking the users and returns """
        images = []
        ask = self.main_dataframe.loc[indexes]["image_url"]

        for i in ask:
            images.append(i)

        self.images = images
        return self.main_dataframe.loc[indexes].index
    
    def active_learning_labeling(self, model, index_labeled_data, X, y, size_uncertain, n_cluster, n):
        """
        Applies labelling phase of Active Learning
            - Fits the model with labeledX and labeledy
            - Takes predictions probabilities of X (all features), {labeled U unlabaled}
            - Creates a sample which contains diverse and uncertain elements for asking to user
            - The sample (diverse, least confident items) are asked to user to be labelled for improvement of model

        Parameters
        ----------
        model: ML model
            used model for the active learning
        index_labeled_data: list
            indexes known labels
        X: DataFrame
            features data
        y: Series
            target data
        size_uncertain: int
            total size of uncertain elements
        n_cluster: int
            creates n_cluster times cluster
        n: int
            takes n element for each clusters

        Returns
        ----------
        list
            image list which contains url of images to be asked
        """
        # fits with labeled data
        model.fit(X.loc[index_labeled_data], y.loc[index_labeled_data])
        
        # gets predictions probs
        pred_probs = model.predict_proba(X)

        # finds uncertain sample
        indexes_uncertain_sample = self.create_sample(X, pred_probs, size_uncertain, n_cluster, n)

        # asks user
        data_ask = X.loc[indexes_uncertain_sample]
        indexes_asked_img = self.ask_to_user(data_ask.index)
        
        return indexes_asked_img

    def active_learning_updating(self, index_labeled_data, y, asked_idx, labels_asked):
        """
        Applies updating phase of Active Learning
        After getting new labels, updates variables
            - Updates y with new labels
            - Updates labeled data

        Parameters
        ----------
        index_labeled_data: list
            list that contains indexes of labeled data
        y: Series
            target data
        asked_idx: list
            indexes of asked items
        labels_asked: list
            labels of asked items

        Returns
        ----------
        list, Series
            indexes of updated X, updated y
        """
        # update y
        y.loc[asked_idx] = labels_asked
        
        # extends labeled data with responses of users
        labeled_index_list = list(index_labeled_data)
        for j in list(asked_idx):
            labeled_index_list.append(j)

        return labeled_index_list, y

    def fit(self, model, labeled_data, X, y):
        """
        After Active Learning processes is done, a new model is fitted with collected(labelled from user) data

        Parameters
        ----------
        model: ML model
            used model in active learning step
        labeled_data: list
            indexes of labeled data
        X: DataFrame
            features data
        y: Series
            target data

        Returns
        ----------
        ML model, DataFrame, Series
            fitted model, updated X and updated y
        """

        # fits models
        model.fit(X.loc[labeled_data], y.loc[labeled_data])

        # drops known data
        X_dropped = X.drop(index=labeled_data)
        y_dropped = y.drop(index=labeled_data)
        
        return model, X_dropped, y_dropped

    def scoring(self, model, data):
        """
        Gets prediction probabilities as scores

        Parameters
        ----------
        model: ML model
            used model in active learning step
        data: DataFrame
            unlabelled data

        Returns
        ----------
        dict
            sorted scoring dictionary

        """
        # dict_ => {index, (isLiked, score)}
        dict_  = {}
        dict_2 = {}
        for k, i in enumerate(model.predict_proba(data)):
            if i[1] >= i[0]:
                dict_[k] = (1, max(i))
                dict_2[k] = (max(i))
            else:
                dict_[k] = (-1, max(i))
                dict_2[k] = (-1 * max(i))
        
        dict_idx_class_score = {k: v for k, v in sorted(dict_.items(), key=lambda item: item[1][1], reverse=True)}
        dict_idx_score       = {k: v for k, v in sorted(dict_2.items(), key=lambda item: item[1], reverse=True)}

        return dict_idx_score



