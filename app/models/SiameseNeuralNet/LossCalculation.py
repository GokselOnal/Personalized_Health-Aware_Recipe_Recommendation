import numpy as np
import pandas as pd
import pickle
import os
import torch
import torch.nn.functional as F


class ContrastiveLoss(torch.nn.Module):
    def init(self, margin=2.0):
        super(ContrastiveLoss, self).init()
        self.margin = margin
        self.outputs = None

    def load_outputs(self):
        pickle_in = open(os.path.abspath(os.getcwd()) + "\\final_outputs.pkl", "rb")
        self.outputs = pickle.load(pickle_in)

    def forward(self, output1, output2, label):

      euclidean_distance = F.pairwise_distance(output1, output2, keepdim = True)
      loss_contrastive = torch.mean((1-label) * torch.pow(euclidean_distance, 2) +
                                    (label) * torch.pow(torch.clamp(self.margin - euclidean_distance, min=0.0), 2))

      return loss_contrastive

    def similarity_scores(self, outputs, target_index):
        final_matrix = np.empty((1, 36228))
        for i in range(len(outputs)):
            euclidean_distance = F.pairwise_distance(outputs[target_index], outputs[i])
            final_matrix[0][i] = euclidean_distance
        return final_matrix

    def most_similars(self, final_matrix, n):
        data_f = pd.DataFrame(final_matrix)
        list_idx = list(data_f.T.sort_values(ascending=True, by=0)[1:n+1].index)
        return list_idx