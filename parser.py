import csv

class productionRule:
    def __init__(self, idx, lhs, rhs):
        self.idx = idx
        self.lhs = lhs
        self.rhs = rhs


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.action = {}
        self.goto = {}
        self.prodRules = {}
        self.load_slr_table()
        self.load_grammar()
        #symbol table
        self.symbol_table = {}
        self.type_error = False
        #function param scope stack
        self.fun_scope = []

    def load_grammar(self):
        #load grammar rules
        gf = "level4_grammar.txt"
        f = open(gf, "r")
        idx = 0
        for line in f:
            line = line.strip()
            #split lhs and rhs
            s = line.split("->")
            left = s[0].strip()
            lhs = left.split()[-1]
            rhs_str = s[1].strip()

            #split rhs symbols
            if rhs_str == "":
                rhs = []
            else:
                rhs = rhs_str.split()

            #store rule by order
            self.prodRules[idx] = productionRule(idx, lhs, rhs)
            idx += 1
        f.close()

    def load_slr_table(self):
        #load slr table
        slr = "level4_parsing_table.csv"
        f = open(slr, "r")
        rows = list(csv.reader(f))
        f.close()

        #get header line
        head = rows[1]
        #find split position
        end_idx = head.index("$")
        z_idx = head.index("Z")
        c_idx = head.index("C")
        terminal = head[1:end_idx + 1]
        nonterminal = head[z_idx:c_idx + 1]

        #read each state row
        for r in rows[2:]:
            state = int(r[0])
            self.action[state] = {}
            self.goto[state] = {}

            #fill action part
            i = 1
            for t in terminal:
                cell = r[i].strip()
                if cell != "":
                    self.action[state][t] = cell
                i += 1

            #fill goto part
            j = z_idx
            for nt in nonterminal:
                cell = r[j].strip()
                if cell != "":
                    self.goto[state][nt] = int(cell)
                j += 1

    def parse(self):
        #slr main loop
        #init stacks
        state_stack = [0]
        node_stack = []
        i = 0
        self.symbol_table = {}
        self.type_error = False
        self.fun_scope = []

        while True:
            state = state_stack[-1]
            #read next token
            raw_name = self.tokens[i].name
            #table uses id for identifier
            table_name = "id" if raw_name == "identifier" else raw_name

            act = self.action[state].get(table_name, "")
            #no action => syntax error
            if act == "":
                return None

            #accept
            elif act == "acc":
                root_node = node_stack.pop()
                final_node = {"name": "Z", "type": root_node.get("type", "NA"), "children": [root_node]}

                parse_tree = self.strip_parse(final_node)
                type_tree = self.strip_type(final_node)

                forest = root_node.get("forest", [])
                ast_forest = []
                for t in forest:
                    t2 = self.strip_ast(t)
                    if t2 is not None:
                        ast_forest.append(t2)

                return parse_tree, type_tree, ast_forest

            #shift
            elif act[0] == "s":
                #shift:push next state
                next_state = int(act[1:])
                state_stack.append(next_state)

                lex = self.tokens[i].lexeme

                #bind params before parsing function body
                if raw_name == "to":
                    #stack ends with ... f id maps i
                    i_node = node_stack[-1]
                    ids = i_node.get("ids", [])
                    Ft = node_stack[-4].get("type", "NA")
                    fname_node = node_stack[-3]
                    fname = fname_node.get("lexeme", "")
                    self.symbol_table[fname] = Ft
                    fname_node["type"] = Ft

                    parts = Ft.split("->") if Ft is not None else []
                    dom = parts[:-1] if len(parts) >= 2 else []

                    if len(dom) != len(ids):
                        self.type_error = True
                        self.fun_scope.append({})
                    else:
                        #save old bindings and bind new
                        old = {}
                        m = {}
                        for k in range(len(ids)):
                            nm = ids[k]
                            old[nm] = self.symbol_table.get(nm, None)
                            self.symbol_table[nm] = dom[k]
                            m[nm] = dom[k]
                        self.fun_scope.append(old)
                        #fill i node type
                        if len(dom) > 0:
                            i_node["type"] = "->".join(dom)
                        #also fill type on identifier terminals inside i subtree
                        stack = [i_node]
                        while len(stack) > 0:
                            cur = stack.pop()
                            if isinstance(cur, dict):
                                if cur.get("name") == "identifier":
                                    nm = cur.get("lexeme", "")
                                    if nm in m:
                                        cur["type"] = m[nm]
                                kids = cur.get("children", [])
                                if kids is not None:
                                    for ch in kids:
                                        stack.append(ch)
                        cur_i = i_node
                        idx = 0
                        while isinstance(cur_i, dict) and cur_i.get("name") == "I":
                            remain = dom[idx:]
                            if len(remain) == 0:
                                break
                            if len(remain) == 1:
                                cur_i["type"] = remain[0]
                            else:
                                cur_i["type"] = "->".join(remain)

                            kids = cur_i.get("children", [])
                            #rule12:i->identifier 
                            if isinstance(kids, list) and len(kids) >= 3 and isinstance(kids[2], dict) and kids[2].get("name") == "I":
                                cur_i = kids[2]
                                idx += 1
                                continue
                            break

                #terminal type(for literals only)
                t = "NA"
                if raw_name == "num_lit":
                    t = "num"
                elif raw_name == "bool_lit":
                    t = "bool"

                #terminal ast
                ast_node = None

                #remove tokens from ast
                if raw_name in {",", ".", "(", ")", "be", "maps", "to", "then", "else"}:
                    ast_node = None
                #literal/id in ast use lexeme as name
                elif raw_name in ("num_lit", "bool_lit", "identifier"):
                    ast_node = {"name": lex}
                #keywords/operators keep raw token text
                elif raw_name in ("Let", "Compute", "if", "+", "*", "<", "=", ">>"):
                    ast_node = {"name": raw_name}

                node_stack.append({"name": raw_name, "type": t, "lexeme": lex, "ast": ast_node})
                i += 1

            #reduce
            elif act[0] == "r":
                rule_id = int(act[1:])
                rule = self.prodRules[rule_id]

                k = len(rule.rhs)
                children = []
                while k > 0:
                    state_stack.pop()
                    children.insert(0, node_stack.pop())
                    k -= 1

                new_node = self.reduce_semantic(rule_id, rule.lhs, children)

                s = state_stack[-1]
                state_stack.append(self.goto[s][rule.lhs])
                node_stack.append(new_node)

    #semantic rules
    def reduce_semantic(self, rule_id, lhs, children):
        #semantic actions:build parse tree node,propagate types,build ast/forest
        node = {"name": lhs, "type": "NA", "children": children, "ast": None}

        #structure
        #rule0:z->l
        #rule1:l->c
        #rule2:l->s c
        #rule3:s->s d
        #rule4:s->d
        if rule_id in (0, 1, 2, 3, 4):
            if rule_id == 0:
                node["type"] = children[0].get("type", "NA")
                node["forest"] = children[0].get("forest", [])
            elif rule_id == 1:
                node["forest"] = [children[0].get("ast", None)]
            elif rule_id == 2:
                node["forest"] = children[0].get("forest", []) + [children[1].get("ast", None)]
            elif rule_id == 3:
                node["forest"] = children[0].get("forest", []) + [children[1].get("ast", None)]
            else:
                node["forest"] = [children[0].get("ast", None)]
            return node

        #declare variable
        #rule5:d->let t id be e .
        if rule_id == 5:
            declared_type = children[1].get("type", "NA")
            variable_name = children[2].get("lexeme", "")
            expression_type = children[4].get("type", "NA")

            if declared_type != expression_type:
                self.type_error = True
            else:
                self.symbol_table[variable_name] = declared_type
                children[2]["type"] = declared_type

            node["ast"] = {
                "name": "Let",
                "children": [
                    children[1].get("ast"),
                    {"name": variable_name},
                    children[4].get("ast"),
                ],
            }
            return node

        #declare function
        #rule6:d->let f id maps i to e .
        if rule_id == 6:
            declared_function_type = children[1].get("type", "NA")
            function_name = children[2].get("lexeme", "")
            parameter_name_list = children[4].get("ids", [])
            body_type = children[6].get("type", "NA")

            type_parts = declared_function_type.split("->") if declared_function_type is not None else []
            return_type = type_parts[-1] if len(type_parts) >= 1 else "NA"
            if body_type != return_type:
                self.type_error = True

            #restore previous bindings for function params after finishing decl
            if len(self.fun_scope) > 0:
                old_bindings = self.fun_scope.pop()
                for name in old_bindings:
                    if name == function_name:
                        continue
                    if old_bindings[name] is None:
                        if name in self.symbol_table:
                            del self.symbol_table[name]
                    else:
                        self.symbol_table[name] = old_bindings[name]

            ast_children = [children[1].get("ast"), {"name": function_name}, children[4].get("ast"), children[6].get("ast")]
            node["ast"] = {"name": "Let", "children": ast_children}
            return node


        #basic type
        #rule7:t->num
        #rule8:t->bool
        if rule_id in (7, 8):
            if rule_id == 7:
                node["type"] = "num"
                children[0]["type"] = "num"
                node["ast"] = {"name": "num"}
            else:
                node["type"] = "bool"
                children[0]["type"] = "bool"
                node["ast"] = {"name": "bool"}
            return node

        #function type
        #rule9:f->g >> t
        if rule_id == 9:
            parameter_type_list = children[0].get("types", [])
            return_type = children[2].get("type", "NA")
            all_parts = parameter_type_list + [return_type]
            node["type"] = "->".join(all_parts) if len(all_parts) > 0 else "NA"
            node["ast"] = {"name": ">>", "children": [children[0].get("ast"), children[2].get("ast")]}
            return node

        #parameter type list
        #rule10:g->t , g
        #rule11:g->t
        if rule_id in (10, 11):
            head_type = children[0].get("type", "NA")
            if rule_id == 10:
                tail_type = children[2].get("type", "NA")
                node["type"] = head_type + "->" + tail_type
                node["types"] = [head_type] + children[2].get("types", [])
                node["ast"] = {"name": ",", "children": [children[0].get("ast"), children[2].get("ast")]}
            else:
                node["type"] = head_type
                node["types"] = [head_type]
                node["ast"] = children[0].get("ast", None)
            return node


        #parameter name list
        #rule12:i->id , i
        #rule13:i->id
        if rule_id in (12, 13):
            head_type = children[0].get("type", "NA")

            if rule_id == 12:
                tail_type = children[2].get("type", "NA")
                node["type"] = head_type + "->" + tail_type
                node["ids"] = [children[0].get("lexeme", "")] + children[2].get("ids", [])
                #ast:param list as comma tree
                node["ast"] = {"name": ",", "children": [children[0].get("ast"), children[2].get("ast")]}
            else:
                node["type"] = head_type
                node["ids"] = [children[0].get("lexeme", "")]
                #ast:single param
                node["ast"] = children[0].get("ast")

            return node



        #if statement
        #rule14:e->if b then a else a
        if rule_id == 14:
            guard_type = children[1].get("type", "NA")
            then_type = children[3].get("type", "NA")
            else_type = children[5].get("type", "NA")

            if guard_type != "bool":
                self.type_error = True
            if then_type != else_type or then_type == "NA":
                self.type_error = True

            node["type"] = then_type
            node["ast"] = {
                "name": "if",
                "children": [
                    children[1].get("ast"),
                    children[3].get("ast"),
                    children[5].get("ast"),
                ],
            }
            return node

        #extra nodes
        #rule15:e->a
        #rule18:b->p
        #rule20:a->m
        #rule22:m->u
        #rule24:u->p
        if rule_id in (15, 18, 20, 22, 24):
            node["type"] = children[0].get("type", "NA")
            node["ast"] = children[0].get("ast", None)
            return node

        #binary optrs
        #rule16:b->a<a
        #rule17:b->a=a
        #rule19:a->a+a
        #rule21:m->m*m
        if rule_id in (16, 17, 19, 21):
            op_map = {16: "<", 17: "=", 19: "+", 21: "*"}
            op = op_map[rule_id]

            left_type = children[0].get("type", "NA")
            right_type = children[2].get("type", "NA")

            if op in ("+", "*", "<"):
                if left_type != "num" or right_type != "num":
                    self.type_error = True
            else:
                if left_type != right_type or left_type not in ("num", "bool"):
                    self.type_error = True

            node["type"] = "bool" if op in ("<", "=") else "num"
            node["ast"] = {"name": op, "children": [children[0].get("ast"), children[2].get("ast")]}
            return node

        #function call
        #rule23:u->u p
        if rule_id == 23:
            function_type = children[0].get("type", "NA")
            argument_type = children[1].get("type", "NA")

            if function_type is None or "->" not in function_type:
                self.type_error = True
                node["type"] = "NA"
            else:
                parts = function_type.split("->")
                if len(parts) < 2:
                    self.type_error = True
                    node["type"] = "NA"
                else:
                    expected_argument_type = parts[0]
                    remaining_type = "->".join(parts[1:])
                    if argument_type != expected_argument_type:
                        self.type_error = True
                        node["type"] = "NA"
                    else:
                        node["type"] = remaining_type if remaining_type != "" else "NA"

            node["ast"] = {"name": "Fun", "children": [children[0].get("ast"), children[1].get("ast")]}
            return node

        #literal
        #rule25:p->num_lit
        #rule26:p->bool_lit
        if rule_id in (25, 26):
            if rule_id == 25:
                node["type"] = "num"
            else:
                node["type"] = "bool"
            node["ast"] = children[0].get("ast", None)
            return node

        #id use
        #rule27:p->id
        if rule_id == 27:
            identifier_name = children[0].get("lexeme", "")
            if identifier_name not in self.symbol_table:
                self.type_error = True
                node["type"] = "NA"
                children[0]["type"] = "NA"
            else:
                node["type"] = self.symbol_table[identifier_name]
                children[0]["type"] = node["type"]
            node["ast"] = {"name": identifier_name}
            return node

        #parenthesis
        #rule28:p->( e )
        if rule_id == 28:
            node["type"] = children[1].get("type", "NA")
            node["ast"] = children[1].get("ast", None)
            return node

        #rule29:c->compute e .
        if rule_id == 29:
            node["ast"] = {"name": "Compute", "children": [children[1].get("ast", None)]}
            return node

        return node

    def strip_parse(self, node):
        #strip to parse tree
        if node is None:
            return None
        if "lexeme" in node:
            return {"name": node["name"], "lexeme": node["lexeme"]}
        kids = []
        for ch in node.get("children", []):
            kids.append(self.strip_parse(ch))
        return {"name": node["name"], "children": kids}

    def strip_type(self, node):
        #strip to typed parse tree
        if node is None:
            return None
        if "lexeme" in node:
            return {"name": node["name"], "type": node.get("type", "NA"), "lexeme": node["lexeme"]}
        kids = []
        for ch in node.get("children", []):
            kids.append(self.strip_type(ch))
        return {"name": node["name"], "type": node.get("type", "NA"), "children": kids}

    def strip_ast(self, node):
        #strip to syntax tree
        if node is None:
            return None
        if "children" in node:
            kids = []
            for ch in node.get("children", []):
                ch2 = self.strip_ast(ch)
                if ch2 is not None:
                    kids.append(ch2)
            if len(kids) == 0:
                return {"name": node.get("name", "NA")}
            return {"name": node.get("name", "NA"), "children": kids}
        return {"name": node.get("name", "NA")}
