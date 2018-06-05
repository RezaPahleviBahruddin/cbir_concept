import numpy as np
import colorsys
import cv2
from scipy.spatial import distance
import glob, os, re

class ICICM:
    """ICICM Used for extract texture & color features"""
    def rgb_to_hsv(self, img_file):
        arr = cv2.cvtColor(cv2.imread(img_file), cv2.COLOR_BGR2RGB)
        row,col,channel = arr.shape 
        h_mat = []
        s_mat = []
        v_mat = []
        for x in range(row):
            for y in range(col):
                r,g,b = arr[x][y]
                h,s,v = colorsys.rgb_to_hsv(r,g,b)
                h_mat.append(h)
                s_mat.append(s)
                v_mat.append(v)

        # Split HSV colorspace
        h_ndarray = np.around(np.array(h_mat).reshape([row,col]), decimals=4)
        s_ndarray = np.around(np.array(s_mat).reshape([row,col]), decimals=4)
        v_ndarray = np.around(np.array(v_mat).reshape([row,col]), decimals=4)
        
        return h_ndarray, s_ndarray, v_ndarray

    def quant(self, type, matrix, q_factor, max):
        bins = np.arange(0,max,max/q_factor)
        if type is 'v':
            bins = np.arange(0,max,round(max/q_factor))
        return np.digitize(matrix, bins)-1

    def weight_func_col(self, r1, r2, s, v):
        if v is 0:
            return 0
        weight = np.power(s, r1*np.power(255/v, r2))
        return np.around(weight, decimals=4)

    def weight_func_int(self, r1, r2, s, v):
        return np.around(1 - self.weight_func_col(r1, r2, s, v) , decimals=4)

    def icicm(self, q_factor, matrix1, matrix2):
        icicm = np.zeros([q_factor, q_factor]) 
        h, w = matrix1.shape
        for row in range(h):
            for col in range(w-1):
                icicm[matrix1[row, col], matrix2[row, col+1]] += 1
        return icicm

    def update_icicm_weight(self, icicm, q_factor, r1, r2, hue_quant_matrix, val_quant_matrix, saturation_matrix, intensity_matrix, type):
        h, w = saturation_matrix.shape
        for row in range(h):
            for col in range(w-1):
                if type is 'cc':
                    icicm[hue_quant_matrix[row, col], hue_quant_matrix[row, col+1]] += (self.weight_func_col(r1, r2, saturation_matrix[row][col], intensity_matrix[row][col]) + self.weight_func_col(r1, r2, saturation_matrix[row][col+1], intensity_matrix[row][col+1]))
                if type is 'ci':
                    icicm[hue_quant_matrix[row, col], val_quant_matrix[row, col+1]] += (self.weight_func_col(r1, r2, saturation_matrix[row][col], intensity_matrix[row][col]) + self.weight_func_int(r1, r2, saturation_matrix[row][col+1], intensity_matrix[row][col+1]))
                if type is 'ic':
                    icicm[val_quant_matrix[row, col], hue_quant_matrix[row, col+1]] += (self.weight_func_int(r1, r2, saturation_matrix[row][col], intensity_matrix[row][col]) + self.weight_func_col(r1, r2, saturation_matrix[row][col+1], intensity_matrix[row][col+1]))    
                if type is 'ii':
                    icicm[val_quant_matrix[row, col], val_quant_matrix[row, col+1]] += (self.weight_func_int(r1, r2, saturation_matrix[row][col], intensity_matrix[row][col]) + self.weight_func_int(r1, r2, saturation_matrix[row][col+1], intensity_matrix[row][col+1]))

        return icicm

    def icicm_feature(self, q_factor, hue_matrix, saturation_matrix, intensity_matrix):
        # Quantize H,S value
        h_quant = self.quant('h', hue_matrix, q_factor, 1)
        v_quant = self.quant('v', intensity_matrix, q_factor, 255)

        # define r1 & r2
        r1 = 0.1
        r2 = 0.85

        """compose each of icicm matrix and update their weights"""

        # icicm cc
        icicm_cc = self.icicm(q_factor, h_quant, h_quant)
        icicm_cc = self.update_icicm_weight(icicm_cc, q_factor, r1, r2, h_quant, v_quant, saturation_matrix, intensity_matrix, 'cc')
        # print('ICICM_cc->\n',icicm_cc)

        # icicm ci
        icicm_ci = self.icicm(q_factor, h_quant, v_quant)
        icicm_ci = self.update_icicm_weight(icicm_ci, q_factor, r1, r2, h_quant, v_quant, saturation_matrix, intensity_matrix, 'ci')
        # print('ICICM_ci->\n',icicm_ci)

        # icicm ic
        icicm_ic = self.icicm(q_factor, v_quant, h_quant)
        icicm_ic = self.update_icicm_weight(icicm_ic, q_factor, r1, r2, h_quant, v_quant, saturation_matrix, intensity_matrix, 'ic')
        # print('ICICM_ic->\n',icicm_ic)

        # icicm ii
        icicm_ii = self.icicm(q_factor, v_quant, v_quant)
        icicm_ii = self.update_icicm_weight(icicm_ii, q_factor, r1, r2, h_quant, v_quant, saturation_matrix, intensity_matrix, 'ii')
        # print('ICICM_ii->\n',icicm_ii)

        # concatenate icicm_cc, icicm_ci, icicm_ic, icicm_ii
        return np.vstack((np.hstack((icicm_cc, icicm_ci)),np.hstack((icicm_ic, icicm_ii)))) 

    def manhattan_distance(self, icicm_q, icicm_d):
        h, w = icicm_q.shape
        dim = h*w
        return distance.cityblock(icicm_q.reshape([1, dim]), icicm_d.reshape([1, dim]))

    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, text):
        return [self.atoi(c) for c in re.split('(\d+)', text)]
