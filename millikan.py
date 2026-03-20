import math

class MillikanExperiment:
    def __init__(self):
        # --- 默认物理常量 (可根据实验室具体参数修改) ---
        self.g = 9.8015        # 重力加速度 (m/s^2)
        self.rho_oil = 981.0   # 油的密度 (kg/m^3)
        self.rho_air = 1.205   # 空气密度 (kg/m^3)
        self.eta = 1.83e-5     # 空气粘滞系数 (Pa·s)
        self.d = 5.00e-3       # 极板间距 (m)
        self.l = 1.50e-3       # 下落/上升距离 (m)
        self.b = 6.17e-6       # 修正常数 (m·cmHg)
        self.p = 76.0          # 大气压强 (cmHg)
        self.e_standard = 1.602e-19 # 标准电荷量 (C)

    def calculate_radius(self, tf):
        """计算油滴半径 r"""
        vf = self.l / tf
        r = math.sqrt((9 * self.eta * vf) / (2 * (self.rho_oil - self.rho_air) * self.g))
        return r

    def cunningham_correction(self, q_raw, r):
        """库宁汉修正: q = q_raw / (1 + b/(p*r))^1.5"""
        correction_factor = math.pow(1 + (self.b / (self.p * r)), 1.5)
        return q_raw / correction_factor

    def static_method(self, tf, U):
        """静态法计算"""
        r = self.calculate_radius(tf)
        # q = mgd/U -> m = 4/3 * pi * r^3 * delta_rho
        delta_rho = self.rho_oil - self.rho_air
        mass = (4/3) * math.pi * (r**3) * delta_rho
        q_raw = (mass * self.g * self.d) / U
        q_final = self.cunningham_correction(q_raw, r)
        return r, q_final

    def dynamic_method(self, tf, tr, U):
        """动态法计算"""
        r = self.calculate_radius(tf)
        vf = self.l / tf
        vr = self.l / tr
        # q = 6 * pi * eta * r * (vf + vr) * d / U
        q_raw = (6 * math.pi * self.eta * r * (vf + vr) * self.d) / U
        q_final = self.cunningham_correction(q_raw, r)
        return r, q_final

def main():
    app = MillikanExperiment()
    print("="*30)
    print(" 密里根油滴实验数据处理程序 ")
    print("="*30)
    
    method = input("请选择实验方法 (1.静态法 / 2.动态法): ")
    
    results = []
    
    while True:
        try:
            print("\n请输入数据 (输入 'q' 结束当前输入):")
            tf_input = input("下落时间 tf (s): ")
            if tf_input.lower() == 'q': break
            tf = float(tf_input)
            
            u_input = input("平衡/上升电压 U (V): ")
            U = float(u_input)
            
            if method == '1':
                r, q = app.static_method(tf, U)
            else:
                tr = float(input("上升时间 tr (s): "))
                r, q = app.dynamic_method(tf, tr, U)
            
            n = round(q / app.e_standard)
            e_calc = q / n if n != 0 else 0
            
            results.append({
                'r': r,
                'q': q,
                'n': n,
                'e': e_calc
            })
            print(f"计算结果: 电荷量 q = {q:.4e} C, 估计电荷数 n = {n}")
            
        except ValueError:
            print("输入错误，请输入数字。")

    if results:
        print("\n" + "="*50)
        print(f"{'序号':<4} | {'半径(m)':<10} | {'电荷量(C)':<12} | {'n':<4} | {'单电子电量':<12}")
        print("-" * 50)
        for i, res in enumerate(results):
            print(f"{i+1:<6} | {res['r']:>.4e} | {res['q']:>.4e} | {res['n']:<4} | {res['e']:>.4e}")
        
        avg_e = sum(r['e'] for r in results) / len(results)
        error = abs(avg_e - app.e_standard) / app.e_standard * 100
        print("-" * 50)
        print(f"平均单电子电量 e_avg: {avg_e:.4e} C")
        print(f"相对误差: {error:.2f}%")

if __name__ == "__main__":
    main()