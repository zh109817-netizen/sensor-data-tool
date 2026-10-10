"""D25: 状态机演示任务依赖——A 成功才跑 B；A 失败自动重试（确定性可复现）"""
import time


class TaskStateMachine:
    """状态: IDLE→RUNNING_A→(重试A)→RUNNING_B→SUCCESS/FAILED"""
    def __init__(self, fail_a_first=2, max_retries=3):
        self.state = "IDLE"
        self.fail_a_left = fail_a_first   # A 前 N 次故意失败
        self.retries = 0
        self.max_retries = max_retries

    def run(self, task):
        """模拟执行：A 按配置失败 N 次后成功；B 恒成功"""
        time.sleep(0.2)
        if task == "A" and self.fail_a_left > 0:
            self.fail_a_left -= 1
            return False
        return True

    def step(self) -> bool:
        """执行一次状态转移，返回是否到达终态"""
        s = self.state
        if s == "IDLE":
            self.state = "RUNNING_A"
            print("[RUNNING_A] 任务 A 开始（数据清洗）")
        elif s == "RUNNING_A":
            ok = self.run("A")
            if ok:
                self.state = "RUNNING_B"      # ★ A 成功才进入 B（依赖）
                print(f"[RUNNING_B] A 成功 → 触发 B（依赖满足）")
            else:
                self.retries += 1
                if self.retries <= self.max_retries:
                    print(f"[重试 {self.retries}/{self.max_retries}] A 失败 → 重跑 A")
                    # 状态回到 RUNNING_A（自环边）
                else:
                    self.state = "FAILED"
                    print(f"[FAILED] A 重试 {self.max_retries} 次仍失败 → 整条流水线终止")
        elif s == "RUNNING_B":
            ok = self.run("B")
            self.state = "SUCCESS" if ok else "FAILED"
            print(f"[{self.state}] B 完成: {'成功' if ok else '失败'}")
        return self.state in ("SUCCESS", "FAILED")


sm = TaskStateMachine(fail_a_first=2)      # A 前 2 次失败, 第 3 次成功
print("=== 任务依赖状态机（A 失败重试 → 成功才跑 B）===")
while not sm.step():
    pass
print(f"\n最终状态: {sm.state} | 重试次数: {sm.retries}")
