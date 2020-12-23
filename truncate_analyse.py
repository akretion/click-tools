#!/usr/bin/env python3

from __future__ import print_function

import click
import click_odoo
import yaml


def get_related_table(cr, table):
    cr.execute("""
        SELECT tc.table_name, kcu.column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE constraint_type = 'FOREIGN KEY'
        AND ccu.table_name = %s and ccu.column_name = 'id'""", (table,))
    return cr.fetchall()

def get_table_dependency(cr, table, tree, done, stop=None):
    print("analyse table", table)
    done.append(table)
    tree[table] = []
    if stop in done:
        return
    for rel_table, field in get_related_table(cr, table):
        depend = {}
        tree[table].append({"table": rel_table, "field": field, "tree": depend})
        if rel_table not in done:
            get_table_dependency(cr, rel_table, depend, done, stop)

@click.command()
@click_odoo.env_options(default_log_level="error")
def main(env):
    # Table to analyse
    table = 'account_bank_statement'
    # Stop script (to not wait tooo long) if following table is reach
    stop = "res_company"
    table_dependency = {}
    get_table_dependency(env.cr, table, table_dependency, [], stop)
    res = yaml.dump(table_dependency)
    with open("truncate_analyse.yaml", "w") as f:
        f.write(res)

if __name__ == "__main__":
    main()
