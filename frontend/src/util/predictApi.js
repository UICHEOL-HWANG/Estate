import axios from "axios";

const API_URL = "http://localhost:8009/predict/";

export const predictPriceApi = async ({ floor, districtCode, yearBuilt, area }) => {
  const requestData = {
    query: `${floor},${districtCode},${yearBuilt},${area}`,
  };

  const response = await axios.post(API_URL, requestData, {
    headers: { "Content-Type": "application/json" },
  });

  return response.data;
};
