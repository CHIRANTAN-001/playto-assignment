import Cookies from "js-cookie";

const MERCHANT_ID_KEY = "merchant_id";
const MERCHANT_NAME_KEY = "merchant_name";

export const setMerchantCookie = (id: string, name: string) => {
  Cookies.set(MERCHANT_ID_KEY, id, { expires: 7, sameSite: "strict" });
  Cookies.set(MERCHANT_NAME_KEY, name, { expires: 7, sameSite: "strict" });
};

export const getMerchantId = (): string | undefined => {
  return Cookies.get(MERCHANT_ID_KEY);
};

export const getMerchantName = (): string | undefined => {
  return Cookies.get(MERCHANT_NAME_KEY);
};

export const clearMerchantCookie = () => {
  Cookies.remove(MERCHANT_ID_KEY);
  Cookies.remove(MERCHANT_NAME_KEY);
};
