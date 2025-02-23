import { defineStore } from "pinia";
import { predictPriceApi } from "../util/predictApi";

export const usePredictStore = defineStore("predict", {
  state: () => ({
    floor: "",
    districtCode: "",
    yearBuilt: "",
    area: "",
    predictedPrice: null,
    loading: false,
    errorMessage: "",
    currentYear: new Date().getFullYear(),
  }),
  actions: {
    async predictPrice() {
      this.errorMessage = "";
      
      // ✅ 입력값 검증
      if (!this.floor || !this.districtCode || !this.yearBuilt || !this.area) {
        this.errorMessage = "모든 필드를 입력해주세요.";
        return;
      }

      if (this.yearBuilt < 1900 || this.yearBuilt > this.currentYear) {
        this.errorMessage = "건축년도는 1900년 이후여야 합니다.";
        return;
      }

      if (this.area <= 0) {
        this.errorMessage = "건물면적은 1㎡ 이상이어야 합니다.";
        return;
      }

      this.loading = true;

      try {
        const response = await predictPriceApi({
          floor: this.floor,
          districtCode: this.districtCode,
          yearBuilt: this.yearBuilt,
          area: this.area,
        });

        this.predictedPrice = response.prediction;
      } catch (error) {
        this.errorMessage = "예측에 실패했습니다. 다시 시도해주세요.";
      } finally {
        this.loading = false;
      }
    },
  },
});
