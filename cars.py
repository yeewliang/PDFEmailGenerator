#!/usr/bin/env python3

import json
import locale
import sys
import os
import emails
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle as PS
from reportlab.platypus import Paragraph, Spacer, Table, Image
from reportlab.lib import colors
from reportlab.lib.units import inch

def load_data(filename):
  """Loads the contents of filename as a JSON file."""
  with open(filename) as json_file:
    data = json.load(json_file)
  return data


def format_car(car):
  """Given a car dictionary, returns a nicely formatted name."""
  return "{} {} ({})".format(
      car["car_make"], car["car_model"], car["car_year"])


def process_data(data):
  """Analyzes the data, looking for maximums.

  Returns a list of lines that summarize the information.
  """
  locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
  max_revenue = {"revenue": 0}
  max_sales = {"total_sales": 0}
  most_popular = {}
  #most_popular = {"car": {"car_make":"", "car_model":"","car_year":""}}

  for item in data:
    # Calculate the revenue generated by this model (price * total_sales)
    # We need to convert the price from "$1234.56" to 1234.56
    item_price = locale.atof(item["price"].strip("$"))
    item_revenue = item["total_sales"] * item_price
    if item_revenue > max_revenue["revenue"]:
      item["revenue"] = item_revenue
      max_revenue = item

    # TODO: also handle max sales
    if item["total_sales"] > max_sales["total_sales"]:
      max_sales = item

    # TODO: also handle most popular car_year
    if item["car"]["car_year"] not in most_popular:
      most_popular[item["car"]["car_year"]] = item["total_sales"]
    else:
      most_popular[item["car"]["car_year"]] += item["total_sales"]

  yearMax = max(most_popular, key=most_popular.get)
  #print(yearMax)

  summary = [
    "The {} generated the most revenue: ${}".format(
      format_car(max_revenue["car"]), max_revenue["revenue"]),
    "The {} had the most sales: {}".format(
      format_car(max_sales["car"]), max_sales["total_sales"]),
    "The most popular year was {} with {} sales.".format(
      yearMax, most_popular[yearMax])
  ]

  return summary


def cars_dict_to_table(car_data):
  """Turns the data in car_data into a list of lists."""
  table_data = [["ID", "Car", "Price", "Total Sales"]]
  for item in car_data:
    table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
  return table_data

def main(argv):
  """Process the JSON data and generate a full report out of it."""
  data = load_data("car_sales.json")
  summary = process_data(data)
  print(summary)
  # TODO: turn this into a PDF report
  report = SimpleDocTemplate("/tmp/cars.pdf")
  styles = getSampleStyleSheet()
  table_style = [('GRID', (0,0), (-1,-1), 1, colors.black)]

  report_title = Paragraph("Sales summary for last month", styles["h1"])
  report_spacer = Spacer(1,0.2*inch)
  report_text1 = Paragraph(summary[0], PS('body'))
  report_text2 = Paragraph(summary[1], PS('body'))
  report_text3 = Paragraph(summary[2], PS('body'))
  report_spacer = Spacer(1,0.2*inch)
  report_table = Table(data=cars_dict_to_table(data), style=table_style, hAlign="LEFT")
  report.build([report_title, report_spacer, report_text1, report_text2, report_text3, report_spacer, report_table])

  # TODO: send the PDF report as an email attachment
  sender = "automation@example.com"
  receiver = "{}@example.com".format(os.environ.get('USER'))
  subject = "Sales summary for last month"
  body = '\n'.join(summary)
  message = emails.generate(sender, receiver, subject, body, "/tmp/cars.pdf")
  emails.send(message)


if __name__ == "__main__":
  main(sys.argv)
