#!/usr/bin/env python3

import os
import sys


def get_func_name(line):
    at_sign = line.find("@")
    open_par = line.find("(", at_sign)

    if at_sign == -1 or open_par == -1:
        return None

    return line[at_sign + 1:open_par].strip()


def get_func(lines):
    func = []
    func_name = None
    func_lines = []
    inside_func = False

    for line in lines:
        line = line.split(";", 1)[0].strip()

        if not inside_func:
            if line.startswith("define ") and "{" in line:
                func_name = get_func_name(line)
                func_lines = []
                inside_func = True
            continue

        if line == "}":
            func.append((func_name, func_lines))
            inside_func = False
        elif line != "":
            func_lines.append(line)

    return func


def is_call_instruc(instruc):
    instruc = instruc.strip()

    if "=" in instruc:
        instruc = instruc.split("=", 1)[1].strip()
    words = instruc.split()
    if len(words) == 0:
        return False

    if words[0] == "call":
        return True

    return (
        len(words) > 1
        and words[1] == "call"
    )


def get_blocks(func_lines):
    blocks = []
    labels = {}
    current_block = None

    for line in func_lines:
        if line.endswith(":"):
            label = line[:-1].strip()
            current_block = len(blocks)
            blocks.append([])
            labels[label] = current_block
        else:
            if current_block is None:
                current_block = len(blocks)
                blocks.append([])
                if current_block == 0:
                    labels["entry"] = current_block

            blocks[current_block].append(line)

            if is_call_instruc(line):
                current_block = None

    if len(blocks) == 0:
        blocks.append([])

    return blocks, labels


def get_br_labels(instruc):
    if not instruc.startswith("br "):
        return []

    words = instruc.replace(",", " ").split()
    br_labels = []

    for index in range(len(words) - 1):
        if words[index] == "label":
            label = words[index + 1]
            if label.startswith("%"):
                label = label[1:]
            br_labels.append(label)

    return br_labels


def get_edges(blocks, labels):
    edges = []

    for block_number in range(len(blocks)):
        block = blocks[block_number]
        if len(block) == 0:
            continue

        last_instruc = block[-1]

        if is_call_instruc(last_instruc):
            return_site = block_number + 1
            if return_site < len(blocks):
                edges.append((block_number, return_site, 0))
        else:
            br_labels = get_br_labels(last_instruc)

            for edge_number in range(len(br_labels)):
                label = br_labels[edge_number]
                if label in labels:
                    edges.append((block_number, labels[label], edge_number))

    return edges


def escape_record_label(text):
    escaped = ""

    for char in text:
        if char == "\\":
            escaped += "\\\\"
        elif char == '"':
            escaped += '\\"'
        elif char in "{}|<>":
            escaped += "\\" + char
        else:
            escaped += char

    return escaped


def make_block_label(block):
    if len(block) == 0:
        return ""
    esc_instruc = []

    for instruc in block:
        esc_instruc.append(escape_record_label(instruc))

    return "\\l".join(esc_instruc) + "\\l"


def make_dot_graph(blocks, edges):
    lines = ["digraph {"]

    for block_num in range(len(blocks)):
        label = make_block_label(blocks[block_num])
        lines.append(
            '    Node{} [shape=record,label="{}"];'.format(block_num, label)
        )

    for source, destination, edge_num in edges:
        lines.append(
            "    Node{} -> Node{} [label={}];".format(
                source, destination, edge_num
            )
        )

    lines.append("}")
    return "\n".join(lines) + "\n"


def main():
    

    input_filename = sys.argv[1]
    

    with open(input_filename, "r", encoding="utf-8") as input_file:
        func = get_func(input_file.readlines())


    dots = []

    for func_name, after_name in func:
        blocks, labels = get_blocks(after_name)
        edges = get_edges(blocks, labels)
        dot = make_dot_graph(blocks, edges)
        output_filename = func_name + ".dot"

        with open(output_filename, "w", encoding="utf-8") as output_file:
            output_file.write(dot)

        dots.append(dot)

    if len(dots) == 1:
        print(dots[0], end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
