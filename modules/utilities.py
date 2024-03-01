import streamlit as st
from dotenv import load_dotenv
import os
import openai
from time import time
from dotenv import load_dotenv
from datetime import datetime
import time
import sqlite3
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer, util
import numpy as np