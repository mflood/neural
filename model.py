
class InputNode(object):

    def __init__(self, name, weight_adj):
        self.name = name
        self.weight_multiplier = 1
        self.value_mesh_node_dict = {}

    def __repr__(self):
        ret = "Input %s:\n" % self.name
        for key in self.value_mesh_node_dict:
            ret += "  (%s) %s" % (key, self.value_mesh_node_dict[key])
        return ret

    def evaluate(self, value):
        if value in self.value_mesh_node_dict:
            mesh_node = self.value_mesh_node_dict[value]
            mesh_node.excite(self.weight_multiplier)

class RangeInputNode(object):

    def __init__(self, name, weight_adj):
        self.name = name
        self.weight_multiplier = weight_adj
        self.range_mesh_node_list = []

    def __repr__(self):
        ret = "RangeInput %s:\n" % self.name
        for stuff in self.range_mesh_node_list:
            ret += "  (%s-%s) %s" % (stuff['min'], stuff['max'], stuff['node'])
        return ret

    def evaluate(self, value):
        for item in self.range_mesh_node_list:
            if float(item['min']) <= float(value) and float(value) < float(item['max']):
                mesh_node = item['node']
                mesh_node.excite(self.weight_multiplier)

class MeshNode(object):

    def __init__(self, name):
        self.output_links = []
        self.name = name
    def __repr__(self):
        ret = ""
        ret += "msh %s:\n" % self.name
        for link in self.output_links:
            ret += "     %s\n" % link
        return ret

    def prune(self):
        sorted_list = sorted(self.output_links, key=lambda k: 0 - k.emit_percent) 
        for link in sorted_list:
            if link.emit_percent < .15:
                link.emit_percent = 0

    def reset(self):
        for link in self.output_links:
            link.fire_state = 0

    def excite(self, weight_multiplier):
        for link in self.output_links:
            link.fire(weight_multiplier)

class Link(object):

    def __init__(self, source_node, target_node):
        self.source_node = source_node
        self.target_node = target_node
        self.num_good_fires = 0.0
        self.num_bad_fires = 0.0
        self.emit_percent = 0.0
        self.fire_state = 0.0
        self.weight = 0.0

    def __repr__(self):
        ret = "target: %s fire: %s wt: %s" % (self.target_node.name, self.fire_state, self.emit_percent)
        return ret

    def fire(self, weight_multiplier):
        self.fire_state = 1
        self.target_node.add_weight(self.emit_percent * weight_multiplier)
        
class TargetNode(object):

    def __init__(self, name, weight_adj):
        self.name = name
        self.weight_adj = weight_adj
        self.input_links = []
        self.weight = 0.0

    def reset(self):
        self.weight = 0.0

    def final_weight(self):

        return self.weight * self.weight_adj

    def add_weight(self, weight):
        self.weight += weight

    def train_up(self):
        for link in self.input_links:
            if link.fire_state:
                link.num_good_fires += 1
                link.emit_percent = link.num_good_fires / (link.num_bad_fires + link.num_good_fires)

    def train_down(self):
        for link in self.input_links:
            if link.fire_state:
                link.num_bad_fires += 1
                link.emit_percent = link.num_good_fires / (link.num_bad_fires + link.num_good_fires)


class Model(object):

    def __init__(self):
        self.input_node_dict = {}
        self.mesh_nodes = []
        self.target_nodes = []

    def __repr__(self):
        ret = ""
        for key in self.input_node_dict:
            ret += "%s\n" % self.input_node_dict[key]
        return ret
    
    def reset(self):
        for t_node in self.target_nodes:
            t_node.reset()
        for m_node in self.mesh_nodes:
            m_node.reset()

    def prune(self):
        for m_node in self.mesh_nodes:
            m_node.prune()

    def evaluate(self, input_set):
        self.reset()
        #print "Evalue: %s" % input_set
        for key in input_set:
            if key in self.input_node_dict:
                self.input_node_dict[key].evaluate(input_set[key])


        return_list = []
        for node in self.target_nodes:
            bit = {'target': node.name, 'value': node.weight, 'adjusted_value': node.final_weight()}
            return_list.append(bit)
        
        return_list = sorted(return_list, key=lambda k: 0 - k['adjusted_value']) 
        return return_list

    def train(self, input_set, target_value_name):
        target_value = input_set[target_value_name]
        r = self.evaluate(input_set)
        #print "Train: %s %s => %s" % (input_set, target_value, r)
        for node in self.target_nodes:
            #print "comp %s to %s" % (node.name, target_value)
            if node.name == target_value:
                node.train_up()
            else:
                node.train_down()

    def add_range_input(self, name, range_list, weight_adj):
        in_node = RangeInputNode(name, weight_adj)
        self.input_node_dict[name] = in_node
        for the_range in range_list:
            mesh_node = MeshNode("%s=%s-%s" % (name, the_range['min'], the_range['max']))
            self.mesh_nodes.append(mesh_node)
            self._connect_mesh_node(mesh_node)
            info_dict = {'min': the_range['min'],
                         'max': the_range['max'],
                         'node': mesh_node,
                        }
            in_node.range_mesh_node_list.append(info_dict)

    def add_input(self, name, value_list, weight_adj):
        in_node = InputNode(name, weight_adj)
        self.input_node_dict[name] = in_node
        for value in value_list:
            mesh_node = MeshNode("%s=%s" % (name, value))
            self.mesh_nodes.append(mesh_node)
            self._connect_mesh_node(mesh_node)
            in_node.value_mesh_node_dict[value] = mesh_node
        

    def _connect_mesh_node(self, mesh_node):
        for target_node in self.target_nodes:
            link = Link(mesh_node, target_node) 
            mesh_node.output_links.append(link)
            target_node.input_links.append(link)

    def _connect_target_node(self, target_node):
        for mesh_node in self.mesh_nodes:
            link = Link(mesh_node, target_node) 
            mesh_node.output_links.append(link)
            target_node.input_links.append(link)

    def add_target(self, target_name, weight_adj):
        target_node = TargetNode(target_name, weight_adj)
        self.target_nodes.append(target_node)
        self._connect_target_node(target_node)
        
if __name__ == "__main__":
    mesh = Model()
    mesh.add_input("d1", [0,1])
    mesh.add_input("d2",[0,1])

    mesh.add_target("even")
    mesh.add_target("odd")

    print mesh


    mesh.train({'d1':1, 'd2':1}, "even")
    def t():
        mesh.train({'d1':1, 'd2':1}, "even")
        mesh.train({'d1':1, 'd2':0}, "even")
        mesh.train({'d1':0, 'd2':0}, "odd")
        mesh.train({'d1':0, 'd2':0}, "odd")

    for x in range(100):
        t()
    print mesh

