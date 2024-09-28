import axios from 'axios';

axios.get('https://www.googleapis.com/civicinfo/v2/elections')
  .then(response => {
    // Handle the successful response
    // console.log(response.data);
  })
  .catch(error => {
    // Handle any errors
    console.error(error);
  });

