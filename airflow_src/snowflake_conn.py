""" Script that details the database manager used """
import os

import pandas as pd
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, exc
from urllib import parse
import config


class DBManager:
    """ Database manager """

    def __init__(self, database):
        """ Constructor """
        self.database = database
        self.db_config_settings = self.get_settings()
        self.engine = self.generate_connection()

    @staticmethod
    def get_settings():
        """ Function to get database settings """
        settings = {
                "account": config.SF_DB_ACCOUNT,
                "user": config.SF_DB_USER,
                "password": config.SF_DB_PASSWORD,
                "schema": config.SF_DB_SCHEMA,
                "database": config.SF_DB_DATABASE,
                "warehouse": config.SF_DB_WAREHOUSE,
                "role": config.SF_DB_ROLE
            }

        return settings

    def generate_connection(self):
        """ Function to generate database connection """
        engine = create_engine(URL(
                account=self.db_config_settings['account'],
                user=self.db_config_settings['user'],
                password=self.db_config_settings['password'],
                database=self.db_config_settings['database'],
                warehouse=self.db_config_settings['warehouse'],
                role=self.db_config_settings['role']))

        return engine

    def execute_query(self, query):
        """ Execute the Query"""
        return self.engine.execute(query)


