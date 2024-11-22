export const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0];
};

export const parseDate = (dateStr: string): Date => {
    return new Date(dateStr);
};

export const getDefaultDateRange = (): { startDate: Date; endDate: Date } => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setFullYear(endDate.getFullYear() - 1);
    
    return { startDate, endDate };
}; 