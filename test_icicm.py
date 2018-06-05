from module.icicm import ICICM

icicm = ICICM()
q_factor = 8
h_q,s_q,v_q = icicm.rgb_to_hsv('/run/media/reza/Data/corel_dataset/CorelDB/sc_autumn/150064.jpg')
icicm_q = icicm.icicm_feature(q_factor, h_q, s_q, v_q)
print('ICICM_query->\n',icicm_q)

path = '/run/media/reza/Data/corel_dataset/CorelDB/sc_autumn/*.jpg'
img_path = sorted([x for x in glob.glob(path)], key=icicm.natural_keys)
sim_mat = []
for idx, img in enumerate(img_path):
    print('Process image-> ', idx)
    h_d,s_d,v_d = icicm.rgb_to_hsv(img)
    icicm_d = icicm.icicm_feature(q_factor, h_d, s_d, v_d)
    sim_mat.append(icicm.manhattan_distance(icicm_q, icicm_d))

sorted_similarity = np.argsort(np.array(sim_mat))
for idx in sorted_similarity[:4]:
    print(img_path[idx])    