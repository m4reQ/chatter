import axios, { Axios, AxiosError, AxiosHeaders, Method, RawAxiosRequestHeaders, ResponseType } from "axios";
import { UserActivityStatus } from "./User";
import { NavigateFunction, replace } from "react-router";

const api = axios.create({
    baseURL: process.env.API_BASE_URL,
});

export function setupInterceptors(navigate: NavigateFunction) {
    api.interceptors.response.use(
        response => response,
        error => {
            if (error instanceof AxiosError && error?.status === 401) {
                localStorage.removeItem("userJWT");
                navigate("/login", {replace: true});
            } else {
                return Promise.reject(error);
            }
        }
    )
}

export default api;

export enum RegisterResult {
    SUCCESS,
    INVALID_ENCODING,
    ALREADY_EXISTS,
    PASSWORD_INVALID,
    EMAIL_INVALID,
    EMAIL_DOESNT_EXIST,
    INTERNAL_ERROR,
};

export enum LoginResult {
    SUCCESS,
    INVALID_CREDENTIALS,
    UNAUTHORIZED_CLIENT,
    INTERNAL_ERROR,
};

interface RequestConfig {
    method: Method;
    url: string;
    data?: any;
    headers?: RawAxiosRequestHeaders | AxiosHeaders;
    responseType?: ResponseType;
    params?: any;
};

interface RequestConfigWithJWT extends RequestConfig {
    jwt: string;
}

export function makeAPIRequest({method, url, data = undefined, headers = undefined, responseType = "json", params = undefined}: RequestConfig) {
    return api.request({
        method: method,
        baseURL: process.env.API_BASE_URL,
        url: url,
        data: data,
        responseType: responseType,
        headers: {"X-Api-Key": process.env.API_KEY, ...headers},
        params: params,
    });
}

export function makeAPIRequestWithJWT({jwt, method, url, data = undefined, headers = undefined, responseType = "json", params = undefined}: RequestConfigWithJWT) {
    return makeAPIRequest({
        method: method,
        url: url,
        data: data,
        headers: {...headers, "Authorization": "Bearer " + jwt},
        responseType: responseType,
        params,
    });
}

export async function postRegisterRequest(username: string, email: string, password: string) {
    const response = await makeAPIRequest({
        method: "POST",
        url: "/auth/register",
        data: {
            username: username,
            email: email,
            password: password,
        },
    });
    
    switch (response.status) {
        case 201:
            return RegisterResult.SUCCESS;
        case 415:
            return RegisterResult.INVALID_ENCODING;
        case 409:
            return RegisterResult.ALREADY_EXISTS;
        case 400:
            switch (response.data.error_code as string) {
                case "password_format_invalid":
                    return RegisterResult.PASSWORD_INVALID;
                case "email_invalid":
                    return RegisterResult.EMAIL_INVALID;
                case "email_doesnt_exist":
                    return RegisterResult.EMAIL_DOESNT_EXIST;
            }        
    }

    // 500
    return RegisterResult.INTERNAL_ERROR;
}

export async function postValidateUserJWT(jwt: string) {
    const response = await makeAPIRequest({
        method: "POST",
        url: `/auth/validate-jwt`,
        headers: {"Authorization": "Bearer " + jwt},
    });

    return response.status === 204;
}

export async function putSetUserActivityStatus(jwt: string, status: UserActivityStatus) {
    return makeAPIRequest({
        method: "PUT",
        url: `/user/change-activity-status/${status}`,
        headers: {"Authorization": "Bearer " + jwt},
    });
}

export async function putRefreshUserActivity(jwt: string) {
    return makeAPIRequest({
        method: "PUT",
        url: "/user/refresh-activity",
        headers: {"Authorization": "Bearer " + jwt},
    });
}

export async function postConfirmEmail(code: string) {
    return makeAPIRequest({
        method: "POST",
        url: `auth/verify-email/` + code,
    });
}

export async function postLoginRequest(username: string, password: string): Promise<[LoginResult, string | null]> {
    const response = await makeAPIRequest({
        method: "POST",
        url: "/auth/login",
        data: {
            username: username,
            password: password,
        },
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
    });

    switch (response.status) {
        case 200:
            return [LoginResult.SUCCESS, response.data.access_token as string];
        case 401:
            return [LoginResult.INVALID_CREDENTIALS, null];
        case 400:
            return [LoginResult.UNAUTHORIZED_CLIENT, null];
    }
    
    // response.status === 500
    return [LoginResult.INTERNAL_ERROR, null];
}

export async function getUserProfilePictureURL(userID: number) {
    const response = await makeAPIRequest({
        method: "GET",
        url: `/user/${userID}/profile-picture`,
        responseType: "blob",
    });

    switch (response.status) {
        case 200:
            return URL.createObjectURL(response.data);
        default:
            return undefined;
    }
}

export async function getPasswordValidationRules(): Promise<[RegExp, number]> {
    const response = await makeAPIRequest({
        method: "GET",
        url: "/auth/password-validation-rules",
    });

    if (response.status === 200) {
        return [
            new RegExp(response.data.regex as string),
            response.data.min_password_length as number,
        ];
    } else {
        throw new Error("Failed to get password validation rules.");
    }
}