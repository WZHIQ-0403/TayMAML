from enum import Enum


# 对机器建模
class MachineConfig(object):
    idx = 0

    def __init__(self, cpu_capacity, memory_capacity, disk_capacity, edge_model, cpu=None, memory=None, disk=None):
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.disk_capacity = disk_capacity

        # 设置一个机器建模开关‘edge_model’
        # 需要，edge_model为False
        # 不需要则，edge_model为True，并设置相关参数：带宽、能耗
        if edge_model[0] is False:
            self.bandwidth = 0
            self.energy_consumption_per_unit = edge_model[2]
        else:
            self.bandwidth = edge_model[1]
            self.energy_consumption_per_unit = edge_model[2]

        self.cpu = cpu_capacity if cpu is None else cpu
        self.memory = memory_capacity if memory is None else memory
        self.disk = disk_capacity if disk is None else disk

        self.id = MachineConfig.idx
        MachineConfig.idx += 1


class MachineDoor(Enum):
    TASK_IN = 0
    TASK_OUT = 1
    NULL = 3


class Machine(object):
    def __init__(self, machine_config):
        self.id = machine_config.id
        self.cpu_capacity = machine_config.cpu_capacity
        self.memory_capacity = machine_config.memory_capacity
        self.disk_capacity = machine_config.disk_capacity
        self.cpu = machine_config.cpu
        self.memory = machine_config.memory
        self.disk = machine_config.disk

        # 当机器被建模为边缘计算模式下的虚拟机时设置以下两个值
        self.bandwidth = machine_config.bandwidth
        self.energy_consumption_per_unit = machine_config.energy_consumption_per_unit

        self.cluster = None
        self.task_instances = []
        self.machine_door = MachineDoor.NULL

    def run_task_instance(self, task_instance):
        self.cpu -= task_instance.cpu
        self.memory -= task_instance.memory
        self.disk -= task_instance.disk
        self.task_instances.append(task_instance)
        self.machine_door = MachineDoor.TASK_IN

    def stop_task_instance(self, task_instance):
        self.cpu += task_instance.cpu
        self.memory += task_instance.memory
        self.disk += task_instance.disk
        self.machine_door = MachineDoor.TASK_OUT

    @property
    def running_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if task_instance.started and not task_instance.finished:
                ls.append(task_instance)
        return ls

    @property
    def finished_task_instances(self):
        ls = []
        for task_instance in self.task_instances:
            if task_instance.finished:
                ls.append(task_instance)
        return ls

    def attach(self, cluster):
        self.cluster = cluster

    def accommodate(self, task):
        return self.cpu >= task.task_config.cpu and \
               self.memory >= task.task_config.memory and \
               self.disk >= task.task_config.disk

    @property
    def feature(self):
        return [self.cpu, self.memory, self.disk]

    @property
    def capacity(self):
        return [self.cpu_capacity, self.memory_capacity, self.disk_capacity]

    @property
    def state(self):
        return {
            'id': self.id,
            'cpu_capacity': self.cpu_capacity,
            'memory_capacity': self.memory_capacity,
            'disk_capacity': self.disk_capacity,
            'cpu': self.cpu / self.cpu_capacity,
            'memory': self.memory / self.memory_capacity,
            'disk': self.disk / self.disk_capacity,
            'running_task_instances': len(self.running_task_instances),
            'finished_task_instances': len(self.finished_task_instances)
        }

    def __eq__(self, other):
        return isinstance(other, Machine) and other.id == self.id
