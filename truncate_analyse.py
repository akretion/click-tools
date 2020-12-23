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
    return [x[0] for x in cr.fetchall()]

def get_table_dependency(cr, table, tree, done):
    print("analyse table", table)
    done.append(table)
    tree[table] = {}
    for rel_table in get_related_table(cr, table):
        if rel_table not in done:
            get_table_dependency(cr, rel_table, tree[table], done)

@click.command()
@click_odoo.env_options(default_log_level="error")
def main(env):
    table = 'account_bank_statement'
    table_dependency = {}
    get_table_dependency(env.cr, table, table_dependency, [])
    res = yaml.dump(table_dependency)
    with open("truncate_analyse.yaml", "w") as f:
        f.write(res)

if __name__ == "__main__":
    main()
