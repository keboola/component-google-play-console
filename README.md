Google Play Console
=============

This component extracts various reports from the Google Play Console API, supporting both full and incremental data loading with configurable date ranges.

## Prerequisites

To use this component, you need:

1. **Google Cloud Platform Service Account**
   - Create a service account with access to Google Play Console API: [Create Service Account](https://cloud.google.com/iam/docs/service-accounts-create#console)
   - Generate a service account key in JSON format: [Create Service Account Key](https://cloud.google.com/iam/docs/keys-create-delete#console)

2. **Google Play Console Access**
   - In Google Play Console, navigate to "Users and permissions"
   - Click "Invite new users" and enter the service account email address
   - Grant the following permissions:
     - "View app information and download bulk reports (read-only)"
     - "View financial data, orders, and cancellation survey responses"
   - Click "Invite User"

3. **Google Cloud Storage Bucket ID**
   - In Google Play Console, navigate to "Download reports"
   - Select any report and click "Copy Cloud Storage URI"
   - From the URI `gs://name_of_your_bucket_123456789/earnings/`, extract only the bucket name: `name_of_your_bucket_123456789`

Features
========

| **Feature**             | **Description**                               |
|-------------------------|-----------------------------------------------|
| Generic UI Form         | Dynamic UI form for easy configuration.       |
| Row-Based Configuration | Allows structuring the configuration in rows. |
| Incremental Loading     | Fetch data in new increments.                 |
| Date Range Filter       | Specify the date range for data retrieval.    |

Supported Endpoints
===================

The component currently supports the following Google Play Console reports:
- earnings
- sales
- play_balance_krw
- reviews
- financial-stats/subscriptions
- stats/installs
- stats/crashes
- stats/promotional_content
- stats/ratings
- stats/store_performance

Need additional endpoints? Submit your request to [ideas.keboola.com](https://ideas.keboola.com/).

Configuration
=============
At the configuration component level, insert the contents of the service account’s JSON key.
At the row level configuration, specify the following parameters:
- Bucket ID
- Report Type
- Date Range
- Incremental Loading


Output
======

Provides a list of tables, foreign keys, and schema.

Development
-----------

To customize the local data folder path, replace the `CUSTOM_FOLDER` placeholder with your desired path in the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
volumes:
  - ./:/code
  - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, initialize the workspace, and run the component using the following
commands:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone https://github.com/keboola/component-google-play-console google_play_console
cd google_play_console
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and perform lint checks using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration
===========

For details about deployment and integration with Keboola, refer to the
[deployment section of the developer
documentation](https://developers.keboola.com/extend/component/deployment/).
