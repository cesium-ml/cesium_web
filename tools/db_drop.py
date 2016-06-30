#!/usr/bin/env python

from cesium_app.models import drop_tables, create_tables
print("Dropping tables...")
drop_tables()

print("Re-creating tables...")
create_tables()
