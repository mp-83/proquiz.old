FROM node:17.3-alpine

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
# COPY package*.json ./

# If you are building your code for production
# RUN npm ci --only=production
RUN npm install -g create-react-app

# Bundle app source
COPY . .

EXPOSE 8080
# CMD [ "node", "server.js" ]
CMD tail -f /dev/null
