import { useState } from "react";
import { useQuery } from "react-query";
import { AxiosResponse } from "axios";
import { makeAPIRequestWithJWT } from "../../../../backend.ts";
import { mapQueryResult } from "../../../../utils.ts";
import RoomSearchResultItem from "./RoomSearchResultItem.tsx";
import * as CSS from "./JoinRoomContent.module.css";

interface ChatRoomInfo {
    id: number;
    name: string;
    description?: string;
};

interface RoomsSearchResult {
    query: string;
    offset: number;
    limit: number;
    rooms: ChatRoomInfo[];
};

interface JoinRoomContentProps {
    userJWT: string;
}

function searchRooms(userJWT: string, searchTerm: string) {
    return makeAPIRequestWithJWT({
        jwt: userJWT,
        method: "GET",
        url: `/search/room`,
        params: {
            query: searchTerm,
        }
    }) as Promise<AxiosResponse<RoomsSearchResult>>;
}

export default function JoinRoomContent({userJWT}: JoinRoomContentProps) {
    const [searchTerm, setSearchTerm] = useState("");
    const searchQuery = useQuery(
        ["search-query", userJWT, searchTerm],
        () => searchRooms(userJWT, searchTerm));

    return <div className={CSS.container}>
        <div className={CSS.searchBar}>
            <input
                placeholder="Search chat rooms..."
                onChange={e => {
                    e.preventDefault();
                    setSearchTerm(e.target.value);
                }}></input>
            <img src="/assets/icons/search.svg" />
        </div>
        {mapQueryResult({
            query: searchQuery,
            onLoading: () => <img className={CSS.loadingImg} src="/assets/icons/loading.gif" />,
            onSuccess: result =>
                result.data.rooms.length === 0
                    ? <span>No rooms found...</span>
                    : <div className={CSS.resultsContainer}>
                        {result.data.rooms.map(
                            x => <RoomSearchResultItem
                                key={x.id}
                                id={x.id}
                                name={x.name}
                                description={x.description}
                                userJWT={userJWT}/>)}
                    </div>
        })}
    </div>;
}