from prep_1 import PrepStep1
from prep_2 import PrepStep2
from prep_3 import PrepStep3

step_1 = PrepStep1()
step_1.save_data()

step_2 = PrepStep2()
step_2.save_data()

step_3 = PrepStep3()
step_3.calculate_cosine_sim()
step_3.save_data()
