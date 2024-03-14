# Dance Collaboration Platform - Design Document

## Overview

The Dance Collaboration Platform is designed to provide a space for dancers to collaborate, share videos, and connect with each other. This design document outlines the technical aspects of the platform, explaining the key components and design decisions.


### Frontend

The frontend of the platform is built using the Flask web framework, HTML, CSS, and JavaScript. We adopted a responsive design using Bootstrap to ensure a seamless user experience across different devices. Jinja templating is used to dynamically generate HTML content, providing a flexible and maintainable structure.

### Backend

The backend relies on a SQLite database to store user information, video details, and collaboration data. Python functions handle user authentication, video uploads, and collaboration requests.

### User Authentication

User authentication is implemented using Flask-Login, which manages user sessions and protects certain routes from unauthorized access. Passwords are securely hashed and stored using Werkzeug's security utilities.

## Features and Modules

### User Profiles

Each user has a profile displaying their name, dance styles, and experience level. Profile information is stored in the database and dynamically retrieved based on the logged-in user.

### Video Uploads

Users can upload dance videos using embeded youtube links, which are stored on the server. Video details, including genre, dance style, and username, are associated with each upload in the database.

### Collaboration Requests

Dancers can send collaboration requests to other users. The conversation details, including sender, receiver, and content are also stored in a database, and handed into the messages.html template.

### Playlists/Build

Users can add their favorite dances to their playlist by sending the links of the videos and genres into a playlist database.

## Design Decisions

### Database Schema

The choice of an SQLite database was made for its simplicity and ease of integration with Flask. The database schema is designed to efficiently store user profiles, video data, and collaboration information.

### Responsive Design

The use of Bootstrap and responsive design principles ensures a consistent and user-friendly experience across various devices, including desktops, tablets, and mobile phones.

### Flask Extensions

Flask extensions, such as Flask-Login, were chosen to streamline common tasks and enhance the overall security of the platform.
