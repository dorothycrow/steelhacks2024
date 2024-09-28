import axios from 'axios';

axios.get('https://www.googleapis.com/civicinfo/v2/elections?key=AIzaSyBOx-4M4gD-2KcQZkHqP0wVEfHOqVrv4nY')
  .then(response => {
    // Handle the successful response
    console.log(response.data);
  })
  .catch(error => {
    // Handle any errors
    console.error(error);
  });

