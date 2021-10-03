FROM mcr.microsoft.com/playwright as base

# both files are explicitly required!
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pip install pipenv && \
  apt-get update && \
  apt-get install -y --no-install-recommends gcc python3-dev libssl-dev && \
  pipenv install --deploy --system && \
  apt-get remove -y gcc python3-dev libssl-dev && \
  apt-get autoremove -y && \
  pip uninstall pipenv -y
RUN python -m playwright install

# Install application into container
WORKDIR /app
ENV TEST "scanner"
COPY . .
# Run tests
ENTRYPOINT ["/bin/bash", "start_tests.sh"]