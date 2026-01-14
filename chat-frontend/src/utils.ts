import { ReactNode } from "react";
import { UseQueryResult } from "react-query";


interface MapQueryResultParams<TData, TError> {
    query: UseQueryResult<TData, TError>;
    onLoading?: ReactNode | (() => ReactNode | undefined);
    onSuccess?: ReactNode | ((data: TData) => ReactNode | undefined);
    onError?: ReactNode | ((error: TError) => ReactNode | undefined);
};

export function mapQueryResult<TData, TError>({query, onLoading = undefined, onSuccess = undefined, onError = undefined}: MapQueryResultParams<TData, TError>) {
    switch (query.status) {
        case "loading": {
            if (onLoading) {
                if (onLoading instanceof Function) {
                    return onLoading();
                }

                return onLoading;
            }
            
            return null;
        };
        case "error": {
            if (onError) {
                if (onError instanceof Function) {
                    return onError(query.error);
                }

                return onError;
            }

            return null;
        };
        case "success": {
            if (onSuccess) {
                if (onSuccess instanceof Function) {
                    return onSuccess(query.data);
                }

                return onSuccess;
            }

            return null;
        }
    }

    return null;
}