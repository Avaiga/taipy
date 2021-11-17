if (typeof window.URL.createObjectURL === 'undefined') {
    window.URL.createObjectURL = () => {
      // Do nothing
      // Mock this function for plotly to work
    };
  }
