#!/usr/bin/env python3

import os
import sys


def get_func_name(line):
    at_sign = line.find("@")
    open_parenthesis = line.find("(", at_sign)

    if at_sign == -1 or open_parenthesis == -1:
        return None

    return line[at_sign + 1:open_parenthesis].strip()


def get_func(lines):
    func = []
    func_name = None
    func_lines = []
    inside_func = False

    for line in lines:
        line = line.strip()

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


def get_blocks(function_lines):
    blocks = []
    labels = {}
    current_block = None

    for line in function_lines:
        if line.endswith(":"):
            label = line[:-1].strip()
            current_block = len(blocks)
            blocks.append([])
            labels[label] = current_block
        else:
            if current_block is None:
                current_block = len(blocks)
                blocks.append([])
                labels["entry"] = current_block

            blocks[current_block].append(line)

    if len(blocks) == 0:
        blocks.append([])

    return blocks, labels


def get_br_labels(instruction):
    if not instruction.startswith("br "):
        return []

    words = instruction.replace(",", " ").split()
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

        last_instruction = block[-1]
        br_labels = get_br_labels(last_instruction)

        for edge_number in range(len(br_labels)):
            label = br_labels[edge_number]
            if label in labels:
                edges.append((block_number, labels[label], edge_number))

    return edges


def make_dot_graph(blocks, edges):
    lines = ["digraph {"]

    for block_number in range(len(blocks)):
        lines.append('    Node{} [shape=record,label=""];'.format(block_number))

    for source, destination, edge_number in edges:
        lines.append(
            "    Node{} -> Node{} [label={}];".format(
                source, destination, edge_number
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
