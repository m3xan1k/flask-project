#!/bin/bash

export SECRET_KEY=$1
export SQLALCHEMY_DATABASE_URI=$2
exec $SHELL -i

END

