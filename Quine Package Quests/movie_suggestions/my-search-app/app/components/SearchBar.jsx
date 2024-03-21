'use client';
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SearchBar = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [suggestions, setSuggestions] = useState([]);

    useEffect(() => {
        const fetchSuggestions = async () => {
            if (searchTerm.length > 0) {
                try {
                    const response = await axios.get(`http://localhost:3000/?term=${searchTerm}`);
                    setSuggestions(response.data);
                } catch (error) {
                    console.error(error);
                }
            } else {
                setSuggestions([]);
            }
        };

        fetchSuggestions();
    }, [searchTerm]);

    const handleInputChange = (event) => {
        setSearchTerm(event.target.value);
    };

    const handleSuggestionClick = (suggestion) => {
        console.log('Selected suggestion:', suggestion);
        setSearchTerm(suggestion.title); 
        setSuggestions([]);
        alert(`Selected ${suggestion.title}`)
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <input
            className='text-black'
            type="text"
            placeholder="Enter a movie name..."
            value={searchTerm}
            onChange={handleInputChange}
            style={{ width: '50vw', border: '1px solid #ccc', padding: '5px', borderRadius: '5px' }}
          />
          {suggestions.length > 0 && (
            <ul className="suggestions">
              {suggestions.map((suggestion) => (
                <li
                  key={suggestion.id}
                  onClick={() => handleSuggestionClick(suggestion)}
                  style={{ border: '1px solid #ccc', padding: '5px', borderRadius: '5px', width: '50vw' }}
                >
                  {suggestion.TITLE} | {suggestion.RELEASE_YEAR} | <i>{suggestion.LANGUAGE}</i>
                </li>
              ))}
            </ul>
          )}
        </div>
      );
};

export default SearchBar;
