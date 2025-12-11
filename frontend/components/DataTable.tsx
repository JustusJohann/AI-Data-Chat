import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

interface DataTableProps {
    data: any[];
}

export function DataTable({ data }: DataTableProps) {
    if (!data || !Array.isArray(data) || data.length === 0) {
        return null;
    }

    // Infer columns from the first object
    const columns = Object.keys(data[0]);

    return (
        <Card className="mt-4 w-full overflow-hidden bg-slate-900 border-slate-700 text-slate-100">
            <CardHeader className="py-3 px-4 bg-slate-800">
                <CardTitle className="text-sm font-medium text-slate-400">Data Result</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <ScrollArea className="h-[300px] w-full">
                    <Table>
                        <TableHeader className="bg-slate-800/50 sticky top-0">
                            <TableRow className="hover:bg-slate-800/50 border-slate-700">
                                {columns.map((col) => (
                                    <TableHead key={col} className="text-slate-300 font-bold whitespace-nowrap">
                                        {col}
                                    </TableHead>
                                ))}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {data.map((row, i) => (
                                <TableRow key={i} className="hover:bg-slate-800/30 border-slate-700">
                                    {columns.map((col) => (
                                        <TableCell key={`${i}-${col}`} className="font-mono text-xs whitespace-nowrap">
                                            {row[col]?.toString() ?? <span className="text-slate-600">null</span>}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </ScrollArea>
            </CardContent>
        </Card>
    );
}
